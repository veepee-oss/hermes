import copy
import json
import base64
from operator import itemgetter
from bson import json_util

import api_modules.utils
import utils.s3_utils
import utils.redis_utils


def _is_config_malformed(config_json_input):
    config_json = copy.deepcopy(config_json_input)

    if not "config_name" in config_json: return False, "config_name not specified"
    
    # --- Connection : close
    if not "do_not_modify_connection_header" in config_json: config_json['do_not_modify_connection_header']= False

    # --- SSL
    if not "ssl" in config_json: return False, "ssl not specified"
    if not(isinstance(config_json["ssl"], dict)): return False, "ssl node is not a dictionnary !"

    if not "verify_ssl" in config_json['ssl']: 
        config_json['ssl']['verify_ssl'] = False

    if not config_json['ssl']['verify_ssl'] in [False, True]: return False, "ssl->verify_ssl not boolean !"

    if not "version" in config_json['ssl']: 
        config_json['ssl']['version'] = "PROTOCOL_TLS"

    if not config_json['ssl']['version'] in ["PROTOCOL_TLS", "PROTOCOL_TLSv1","PROTOCOL_TLSv1_1","PROTOCOL_TLSv1_2","PROTOCOL_SSLv2"]: 
        return False, "ssl->version not recognized !"

    if not "ciphers" in config_json['ssl']: 
        config_json['ssl']['ciphers'] = None

    # --- HTTP2
    if not "http2" in config_json: config_json['http2']= 'NO'
    if not config_json['http2'] in ['NO', 'YES','TRY']: return False, "http2 not recognized!"

    # --- URL blacklist / Stopped
    if not "blacklist" in config_json: config_json['blacklist']= []
    if not(isinstance(config_json["blacklist"], list)): return False, "blacklist malformed ! Should be a list !"

    # --- Sites blacklist response
    if not "site_blacklist_response" in config_json: config_json['site_blacklist_response']= ''

    # --- Headers Freeze
    if not "headers_freeze" in config_json: config_json['headers_freeze']= []
    if not(isinstance(config_json["headers_freeze"], list)): return False, "Headers freeze malformed ! Should be a list !"
    for node in config_json['headers_freeze']:
        if not 'host_regex' in node: return False, "Headers freeze malformed ! host_regex not found !"
        if not 'headers' in node: return False, "Headers freeze malformed ! headers not found !"
        if not 'max_requests' in node: return False, "Headers freeze malformed ! max_requests not found !"
        if not(isinstance(node["headers"], list)): return False, "Headers freeze malformed ! headers should be list !"
        if not(isinstance(node["max_requests"], int)): return False, "Headers freeze malformed ! max_requests should be an integer !"

    # --- Headers
    if not "headers" in config_json: config_json['headers']= None

    # --- Data
    if not "data_transformations" in config_json: config_json['data_transformations']= []
    if not(isinstance(config_json["data_transformations"], list)): return False, "data_transformations malformed ! Should be a list !"

    # --- Proxy
    if not "proxy" in config_json: config_json['proxy']= None
    if not config_json['proxy'] is None:
        if not(isinstance(config_json["proxy"], dict)): return False, "proxy should be a dictionnary !"
        if not "js_mode" in config_json['proxy']: config_json['proxy']['js_mode'] = False
        if config_json['proxy']['js_mode'] is True:
            if not 'js_function' in config_json['proxy']: return False, "proxy should have a js_function field !"

    # --- Waterfall
    if not "waterfall_requests" in config_json: config_json['waterfall_requests']= []
    if not(isinstance(config_json["waterfall_requests"], list)): return False, "waterfall_requests malformed ! Should be a list !"

    return True, config_json


def _check_payload_conf(request):
    if not(request.json): return False, "No JSON received by POST method"

    mydata = request.json 

    if not('config' in mydata): return False, "Must specify config"

    config_json = mydata['config']

    if not(isinstance(config_json, dict)): return False, "Not a dictionnary"

    return True, config_json



def create_new(request):
    config_check, config_json = _check_payload_conf(request)
    if config_check is False: return config_json, 400

    config_check, config_json_complete = _is_config_malformed(config_json)
    if config_check is False: return config_json_complete, 400

    list_configs = utils.s3_utils.list_files_prefix("configs/config_id=")
    list_ids = []
    for key in list_configs:
        id_i = int(key.replace('configs/config_id=','').replace('/conf.json',''))
        list_ids.append(id_i)

    if len(list_ids) == 0:
        new_id = 1
    else:
        new_id = max(list_ids) + 1

    new_full_key = "configs/config_id="+str(new_id)+"/conf.json"
    utils.s3_utils.push_string_s3_file(json.dumps(config_json_complete, indent=4, sort_keys=True), new_full_key)

    return api_modules.utils.flask_response_json(True, {"config_id" : new_id})


def update(request, config_id):
    config_check, config_json = _check_payload_conf(request)
    if config_check is False: return config_json, 400

    config_check, config_json_complete = _is_config_malformed(config_json)
    if config_check is False: return config_json_complete, 400

    new_full_key = "configs/config_id="+str(config_id)+"/conf.json"
    utils.s3_utils.push_string_s3_file(json.dumps(config_json_complete, indent=4, sort_keys=True), new_full_key)

    # Delete cached config
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.delete('type=conf_cache/config_id='+str(config_id))

    return api_modules.utils.flask_response_json(True, {"config_id" : config_id})

def list_configs(return_obj = False):
    list_configs = utils.s3_utils.list_files_prefix("configs/config_id=")
    res = []
    for key in list_configs:
        node = {}
        node['key'] = key
        id_i = int(key.replace('configs/config_id=','').replace('/conf.json',''))
        node['id'] = id_i
        res.append(node)


    res = sorted(res, key=itemgetter('id'), reverse=True)

    if return_obj is True: return res

    return api_modules.utils.flask_response_json(True, res)


def delete(config_id):
    # Delete S3
    key_path = "configs/config_id="+str(config_id)+"/conf.json"
    utils.s3_utils.delete_key(key_path)

    # Connect to redis
    redis_client = utils.redis_utils.create_redis_client()
    for key_config_in_redis in redis_client.keys('*/config_id='+str(config_id)+'/*'):
        redis_client.delete(key_config_in_redis)
    return api_modules.utils.flask_response_json(True, 'Deleted !')


def get(config_id):
    key_path = "configs/config_id="+str(config_id)+"/conf.json"
    content = utils.s3_utils.get_content(key_path)
    if content is None:
        return 'Not found !', 404
    else:
        return api_modules.utils.flask_response_json(True, json.loads(content))


def get_meta_data(config_id):
    # Connect to redis
    redis_client = utils.redis_utils.create_redis_client()

    # Cached headers freeze
    res_freeze = [] 
    for cached_key_freeze in redis_client.keys('type=headers_freeze_data/config_id='+str(config_id)+'/*'):
        node = {}
        node['b64_key'] = cached_key_freeze.decode("utf-8").replace('type=headers_freeze_data/config_id='+str(config_id)+'/key=','')

        node['plain_key'] = cached_key_freeze.decode("utf-8").replace('type=headers_freeze_data/config_id='+str(config_id)+'/key=','')
        node['plain_key'] = base64.b64decode(node['plain_key']).decode('ascii')
        
        node['data'] = json_util.loads(redis_client.get(cached_key_freeze))

        node['counter'] = redis_client.get(cached_key_freeze.decode("utf-8") .replace('type=headers_freeze_data','type=headers_freeze_counter'))
        node['counter'] = 0 if node['counter'] is None else int(node['counter'])
        res_freeze.append(node)


    return api_modules.utils.flask_response_json(True, {"headers_freeze_data" : res_freeze})


def headers_freeze_purge(request):
    if not(request.json): return "No JSON received by POST method", 400
    mydata = request.json 
    try:
        config_id = int(mydata['config_id'])
    except:
        return "No config id provided", 400
    if not('b64key' in mydata): return "No b64_key provided", 400

    full_key_to_del_1 = 'type=headers_freeze_data/config_id='+str(config_id)+'/key=' + mydata['b64key']
    full_key_to_del_2 = 'type=headers_freeze_counter/config_id='+str(config_id)+'/key=' + mydata['b64key']

    # Connect to redis
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.delete(full_key_to_del_1)
    redis_client.delete(full_key_to_del_2)
    
    return 'Done !', 200