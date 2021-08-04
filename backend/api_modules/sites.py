import copy
import base64
import binascii
import datetime
import json
from operator import itemgetter

import utils.s3_utils
import utils.redis_utils

import api_modules.utils

def _check_site(request):
    if not(request.json): return False, "No JSON received by POST method"
    mydata = request.json 
    if not('site' in mydata): return False, "Must specify site"
    site_json = mydata['site']
    if not(isinstance(site_json, dict)): return False, "Not a dictionnary"
    return True, site_json

def _is_site_malformed(site_json_input):
    site_json = copy.deepcopy(site_json_input)
    if not "regex" in site_json: return False, "regex not specified"
    if not "blacklist_detection" in site_json: return False, "blacklist_detection not specified"
    return True, site_json


def _encode_name(input_val):
    return binascii.hexlify(base64.b64encode(input_val.encode('utf-8'))).upper().decode()

def decode_name(input_val):
    return base64.b64decode(binascii.unhexlify(input_val.lower())).decode()


def startup_load_sites_s3_to_redis():
    redis_client = utils.redis_utils.create_redis_client()
    
    tmp_res = utils.s3_utils.list_files_prefix("sites/site_hex=", extract_date = True)
    for node_i in tmp_res:
        content_s3_string = utils.s3_utils.get_content(node_i['path'])
        site_json_complete = json.loads(content_s3_string)
        site_json_complete['created_at'] = node_i['created_at'].strftime("%Y-%m-%d %H:%M:%S")

        hashed_name = _encode_name(site_json_complete['regex'])
        redis_client.set('type=site_cached/site_hex='+hashed_name, json.dumps(site_json_complete, indent=4, sort_keys=True))
        redis_client.expire('type=site_cached/site_hex='+hashed_name, 3600 * 24 * 365 * 10) #10 years !

def create_new(request, update = False):
    site_check, site_json = _check_site(request)
    if site_check is False: return site_json, 400

    site_check, site_json_complete = _is_site_malformed(site_json)
    if site_check is False: return site_json_complete, 400

    hashed_name = _encode_name(site_json_complete['regex'])
    regex_name_hex_safe = "sites/site_hex=" + hashed_name +'/conf.json'

    if update is True:
        if (utils.s3_utils.does_key_exists(regex_name_hex_safe) is False): return "Site not found !", 404
    else:
        if (utils.s3_utils.does_key_exists(regex_name_hex_safe) is True): return "Site already exists !", 409
    
    utils.s3_utils.push_string_s3_file(json.dumps(site_json_complete, indent=4, sort_keys=True), regex_name_hex_safe)

    
    redis_client = utils.redis_utils.create_redis_client()
    site_json_complete['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    redis_client.set('type=site_cached/site_hex='+hashed_name, json.dumps(site_json_complete, indent=4, sort_keys=True))
    redis_client.expire('type=site_cached/site_hex='+hashed_name, 3600 * 24 * 365 * 10) #10 years !

    return api_modules.utils.flask_response_json(True, {"site_hex" : hashed_name})


def list_sites(go_fast = False):
    if go_fast is True:
        # Uses Redis
        res = []
        redis_client = utils.redis_utils.create_redis_client()
        for key_site_hex in redis_client.keys('type=site_cached/site_hex=*'):
            node_str = redis_client.get(key_site_hex)
            obj_s = json.loads(node_str)
            obj_s['site_hex'] = _encode_name(obj_s['regex'])
            res.append(obj_s)
        return res

    else:
        # Uses S3
        tmp_res = utils.s3_utils.list_files_prefix("sites/site_hex=", extract_date = True)
        tmp_res = sorted(tmp_res, key=itemgetter('created_at'), reverse=True)
        res = []
        for node in tmp_res:
            node_i = copy.copy(node)
            node_i['site_hex'] = node_i['path'].replace("sites/site_hex=",'').replace('/conf.json','')
            node_i['regex'] = decode_name(node_i['site_hex'])
            res.append(node_i)
        
        return api_modules.utils.flask_response_json(True, res)


def delete_site(request):
    if not(request.json): return "No JSON received by POST method", 400
    mydata = request.json 
    if not('site_hex' in mydata): return "Must specify site", 400
    regex_name_hex_safe = "sites/site_hex=" + mydata['site_hex'] +'/conf.json'

    del_req = utils.s3_utils.delete_key(regex_name_hex_safe)

    
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.delete('type=site_cached/site_hex='+mydata['site_hex'])

    return 'Deleted !', 200


def get_site(site_hex):
    regex_name_hex_safe = "sites/site_hex=" + site_hex +'/conf.json'
    res = utils.s3_utils.get_content(regex_name_hex_safe)
    if res is None:
        return "Not found !", 404
    else:
        return api_modules.utils.flask_response_json(True, json.loads(res))



