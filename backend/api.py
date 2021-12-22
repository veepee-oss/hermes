import os
import sys, getopt
import functools

from flask import Flask, request, g, after_this_request, session
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask_compress import Compress

import utils.config_handler

import api_modules.auth
import api_modules.configs
import api_modules.logs
import api_modules.summary
import api_modules.gzip
import api_modules.test
import api_modules.sites
import api_modules.certificates

import warnings
warnings.filterwarnings("ignore")

# ----------------------------------------------------
# ---------------------- APP -------------------------
# ----------------------------------------------------
SERVER_CONFIG = utils.config_handler.load_json_config()
app = Flask(__name__)
app.secret_key = SERVER_CONFIG['secrets']['secret_app']

auth = HTTPBasicAuth()
CORS(app) #Compress(app)


# ----------------- Compression -----------------
def gzipped(f):
	@functools.wraps(f)
	def view_func(*args, **kwargs):
		@after_this_request
		def zipper(response): return api_modules.gzip.zipper(response, request)
		return f(*args, **kwargs)
	return view_func

# -------------- Certificate Authority ---------------
@app.route('/certificate/public', methods=['GET'])
@auth.login_required
@gzipped
def api_get_public_certificate(): return api_modules.certificates.get_public_certificate()

@app.route('/certificate/private', methods=['GET'])
@auth.login_required
@gzipped
def api_get_private_certificate(): return api_modules.certificates.get_private_certificate()

# ----------------- Authentification -----------------
@auth.verify_password
def verify_password(username_or_token, password = ""): 
	return api_modules.auth.verify_password(username_or_token, password, str(request.remote_addr), request, g)

@app.route('/auth/get_token', methods=['GET'])
@auth.login_required
def auth_get_token(): return api_modules.auth.get_auth_token(g)


# ----------------- Configs ------------------------
@app.route('/configs/new', methods=['POST'])
@auth.login_required
def configs_new(): return api_modules.configs.create_new(request)

@app.route('/configs/list', methods=['GET'])
@auth.login_required
@gzipped
def configs_list(): return api_modules.configs.list_configs()

@app.route('/configs/update/<int:config_id>', methods=['POST'])
@auth.login_required
def configs_update(config_id): return api_modules.configs.update(request, config_id)

@app.route('/configs/delete/<int:config_id>', methods=['GET'])
@auth.login_required
def configs_delete(config_id): return api_modules.configs.delete(config_id)

@app.route('/configs/get/<int:config_id>', methods=['GET'])
@auth.login_required
def configs_get(config_id): return api_modules.configs.get(config_id)

@app.route('/configs/get_meta_data/<int:config_id>', methods=['GET'])
@auth.login_required
def configs_get_meta_data(config_id): return api_modules.configs.get_meta_data(config_id)


@app.route('/configs/headers_freeze/purge', methods=['POST'])
@auth.login_required
def configs_headers_freeze_purge(): return api_modules.configs.headers_freeze_purge(request)


# ----------------- Logs ------------------------
@app.route('/logs/fetch_all_logs', methods=['GET'])
@auth.login_required
@gzipped
def logs_fetch_all_logs(): return api_modules.logs.fetch_all_logs()

@app.route('/logs/fetch_bl_logs', methods=['GET'])
@auth.login_required
@gzipped
def logs_fetch_bl_logs(): return api_modules.logs.fetch_bl_logs()

@app.route('/logs/fetch_xray_log', methods=['POST'])
@auth.login_required
@gzipped
def logs_fetch_xray_log(): return api_modules.logs.fetch_xray_log(request)

@app.route('/logs/flush_redis', methods=['GET'])
@auth.login_required
@gzipped
def logs_flush_redis(): return api_modules.logs.flush_redis()

@app.route('/logs/flush_all_redis', methods=['GET'])
@auth.login_required
@gzipped
def logs_flush_all_redis(): return api_modules.logs.flush_all_redis()

# ----------------- Summary ------------------------
@app.route('/summary', methods=['GET'])
@auth.login_required
@gzipped
def summary(): return api_modules.summary.summary()

@app.route('/summary/<int:config_id>', methods=['GET'])
@auth.login_required
@gzipped
def summary_inted(config_id): return api_modules.summary.summary(config_id)

# ----------------- Tests ------------------------
@app.route('/test_curl', methods=['POST'])
@auth.login_required
@gzipped
def test_curl(): return api_modules.test.test_curl(request)

# ----------------- sites ------------------------
@app.route('/sites/new', methods=['POST'])
@auth.login_required
def sites_new(): return api_modules.sites.create_new(request)

@app.route('/sites/list', methods=['GET'])
@auth.login_required
def sites_list(): return api_modules.sites.list_sites()

@app.route('/sites/delete', methods=['POST'])
@auth.login_required
def sites_delete(): return api_modules.sites.delete_site(request)

@app.route('/sites/update', methods=['POST'])
@auth.login_required
def sites_update(): return api_modules.sites.create_new(request, update = True)

@app.route('/sites/get/<string:site_hex>', methods=['GET'])
@auth.login_required
def sites_get(site_hex): return api_modules.sites.get_site(site_hex)

# ----------------- Ping  ----------------------------
@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def api_root(): return "Welcome !"
	
# ----------------------------------------------------
# ---------------------- LAUNCH ----------------------
# ----------------------------------------------------	
if __name__ == "__main__":
	argv = sys.argv[1:]
	
	try:
		opts, args = getopt.getopt(argv,"hp:c:k:",["port=","cert=","key="])
	except getopt.GetoptError:
		print('Command to run the api: api.py -p <LISTENING_PORT>')
		sys.exit(2)
	
	port = None
	cert_file = None
	key_file = None

	for opt, arg in opts:
		if opt == '-h':
			print('api.py -p <LISTENING_PORT> -c <FULLCHAIN_CERT_FILE_LOCATION_SSL> -k <PRIVATE_KEY_FILE_LOCATION_SSL>')
			sys.exit()
		elif opt in ("-p", "--port"):
			port = arg
		elif opt in ("-c", "--cert"):
			cert_file = arg
		elif opt in ("-k", "--key"):
			key_file = arg

	print("Loading sites into Cache ...")
	api_modules.sites.startup_load_sites_s3_to_redis()

	if port is None: port = 80
	print("Running server with master PID: " + str(os.getpid()) + ' on Port : ' + str(port))

	if (cert_file is None) or (key_file is None):
		app.run(host = "0.0.0.0", port = port, debug=False, threaded = True)
	else:
		app.run(ssl_context=(cert_file,key_file), host = "0.0.0.0", port = port, debug=False, threaded = True)

