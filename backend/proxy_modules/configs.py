import json
import re

import utils.redis_utils
import utils.s3_utils

import proxy_modules.forgery

def fetch_config_live_redis(config_id):
    # Return None if does not exist !
    redis_client = utils.redis_utils.create_redis_client()

    cached_config = redis_client.get('type=conf_cache/config_id='+str(config_id))

    if not cached_config is None:
        return json.loads(cached_config)
    else:
        try:
            # Download from S3
            key_s3 = 'configs/config_id='+str(config_id)+'/conf.json'
            config_objs = json.loads(utils.s3_utils.get_content(key_s3))

            # Cache in redis
            redis_client.set('type=conf_cache/config_id='+str(config_id), json.dumps(config_objs))

            return config_objs
        except Exception as e:
            return None


def extract_proxy_config(json_config):
    # Retuns proxy, auth, proxy_data_dict
    # ----------------------------------------------------
    # proxy can be None or (server, port)
    # auth can be None or (username, password)

    # ----- proxy_data_dict can have 3 formats: ----------
    # case 1 (simple proxy conf no error): {} 
    # case 2 (simple proxy conf  with error): {"error": "port is not an integer !"}
    # case 3 (advanced proxy conf): 
    #           {   
    #                "stdout": "stdout string ...", 
    #                "stderr": "stderr string ...", 
    #                "execerr": "node_js_exec_err string ...", 
    #                "data_carried" : "user data carried from the proxy script execution string" or null
    #           }
    # ----------------------------------------------------

    # Check proxy node !
    if not "proxy" in json_config: return None, None, None, {}
    proxy_node = json_config["proxy"]

    if proxy_node is None: return None, None, None, {}

    # Check mode
    try:
        js_mode = proxy_node['js_mode']
    except:
        js_mode = False
    if not js_mode in [True, False]: js_mode = False

    # We have a proxy !
    if js_mode is True:
        if not "js_function" in proxy_node: return None, None, None, {"error": "js_mode active but no js_function !"}
        if proxy_node['js_function'] is None: return None, None, None, {"error": "js_function is null !"}

        return proxy_modules.forgery.proxy_js_function(proxy_node['js_function'])

    else:
        if (not "host" in proxy_node) or (not "port" in proxy_node): return None, None, None,{}
        try:
            port_used = int(proxy_node['port'])
        except:
            return None, None, None, {"error": "port is not an integer !"}

        proxy_res = (proxy_node['host'], port_used)
        
        if (not "type" in proxy_node): #HTTP by default not to break the existing config
            type=None
        else:
            type=proxy_node["type"]

        if (not "username" in proxy_node) or (not "password" in proxy_node): 
            return proxy_res, None, None, {}
        else:
            if ((proxy_node['username'] is None) and (proxy_node['username'] is None)):
                return proxy_res, None, type, {}
            else:
                return proxy_res, (proxy_node['username'], proxy_node['password']),type, {}


def fetch_site_match_redis(protocol_host_path):
    if protocol_host_path is None: return False, None, None, None
    redis_client = utils.redis_utils.create_redis_client()

    for key_site_hex in redis_client.keys('type=site_cached/site_hex=*'):
        node_str = redis_client.get(key_site_hex)
        obj_s = json.loads(node_str)
        if re.search(obj_s['regex'], protocol_host_path): return True, obj_s['regex'], key_site_hex.decode('utf-8').replace('type=site_cached/site_hex=',''), obj_s['blacklist_detection']
    
    return False, None, None, None