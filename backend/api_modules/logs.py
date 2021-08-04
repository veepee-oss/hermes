import re
from bson import json_util
from flask import Response 

import utils.redis_utils
import api_modules.configs
import api_modules.utils
import api_modules.sites

def explode_key(input_string):
    # config_id=2/domain=www.google.fr/protocol=https/success=1

    # config_id
    config_id = None
    pattern_config_id  = re.compile('(?:config_id=)(.*?)(?:\/)')
    for m in re.finditer(pattern_config_id, input_string):
        config_id = m.group(1)

    # domain
    domain = None
    pattern_domain  = re.compile('(?:domain=)(.*?)(?:\/)')
    for m in re.finditer(pattern_domain, input_string):
        domain = m.group(1)

    # domain
    protocol = None
    pattern_protocol  = re.compile('(?:protocol=)(.*?)(?:\/)')
    for m in re.finditer(pattern_protocol, input_string):
        protocol = m.group(1)

    # domain
    success = None
    pattern_success  = re.compile('(?:success=)(.*?)(?:$)')
    for m in re.finditer(pattern_success, input_string):
        success = m.group(1)

    return config_id, domain, protocol, success

def fetch_all_logs(return_obj = False):
    # Build the res
    res = {}

    # Fetch list of configs
    list_configs = api_modules.configs.list_configs(return_obj = True)
    for config in list_configs:
        res[str(config['id'])] = {}
        res[str(config['id'])]['req_logger'] = []
        res[str(config['id'])]['req_counter'] = []
        res[str(config['id'])]['req_bw_meter'] = []

    # Connect to redis
    redis_client = utils.redis_utils.create_redis_client()

    # Fetch last complete logs
    for key_config_in_redis in redis_client.keys('type=req_logger/config_id=*'):
        config_id = key_config_in_redis.decode("utf-8").replace('type=req_logger/config_id=', '')

        if config_id in res:
            for node_log in redis_client.lrange('type=req_logger/config_id='+ str(config_id), 0, -1):
                res[config_id]['req_logger'].append(json_util.loads(node_log))


    # Fetch consolidated req_counter logs
    for key_config_in_redis in redis_client.keys('type=req_counter/config_id=*'):
        config_id, domain, protocol, success = explode_key(key_config_in_redis.decode("utf-8").replace('type=req_counter/', ''))        
        if config_id in res:
            node_to_push = {"config_id": int(config_id), "domain": domain, "protocol": protocol, "success": int(success), "reqs": int(redis_client.get(key_config_in_redis))}
            res[config_id]['req_counter'].append(node_to_push)

    # Fetch consolidated req_bw_meter logs
    for key_config_in_redis in redis_client.keys('type=req_bw_meter/config_id=*'):
        config_id, domain, protocol, success = explode_key(key_config_in_redis.decode("utf-8").replace('type=req_bw_meter/', ''))        
        if config_id in res:
            node_to_push = {"config_id": int(config_id), "domain": domain, "protocol": protocol, "success": int(success), "req_bw_bytes": int(redis_client.get(key_config_in_redis))}
            res[config_id]['req_bw_meter'].append(node_to_push)


    # Wrap up !
    if return_obj is True: return res
    return Response(
        json_util.dumps(res),
        mimetype='application/json'
    )


def explode_bl_key(input_string):
    # config_id=2/site_hex=4C69706B59584A3065533471/success=1

    # config_id
    config_id = None
    pattern_config_id  = re.compile('(?:config_id=)(.*?)(?:\/)')
    for m in re.finditer(pattern_config_id, input_string):
        config_id = m.group(1)

    # site_hex
    site_hex = None
    pattern_site_hex  = re.compile('(?:site_hex=)(.*?)(?:\/)')
    for m in re.finditer(pattern_site_hex, input_string):
        site_hex = m.group(1)

    # success
    success = None
    pattern_success  = re.compile('(?:success=)(.*?)(?:$)')
    for m in re.finditer(pattern_success, input_string):
        success = m.group(1)

    return config_id, site_hex, success

def fetch_bl_logs(return_obj = False):
    # Build the res
    res = {}

    # Connect to redis
    redis_client = utils.redis_utils.create_redis_client()

    # Add all sites
    all_sites = api_modules.sites.list_sites(go_fast = True)
    for site in all_sites:
        site_hex = site['site_hex']
        res[site_hex] = {}
        res[site_hex]['bl_req_counter'] = []
        res[site_hex]['bl_req_bw_meter'] = []
        res[site_hex]['regex'] = site['regex']
        res[site_hex]['created_at'] = site['created_at']

    for key_bl_req_counter in redis_client.keys('type=bl_req_counter/config_id=*'):
        config_id, site_hex, success = explode_bl_key(key_bl_req_counter.decode("utf-8").replace('type=bl_req_counter/', ''))   

        cache_ct = redis_client.get(key_bl_req_counter)
        cache_ct = int(cache_ct) if not cache_ct is None else 0

        cache_bw = redis_client.get(key_bl_req_counter.replace(b'type=bl_req_counter/',b'type=bl_req_bw_meter/'))
        cache_bw = int(cache_bw) if not cache_bw is None else 0

        node_to_push_counter = {"config_id": int(config_id), "success": int(success), "reqs": cache_ct}
        node_to_push_bw = {"config_id": int(config_id), "success": int(success), "req_bw_bytes": cache_bw}


        if site_hex in list(res.keys()):
            # Could be deleted !
            res[site_hex]['bl_req_counter'].append(node_to_push_counter)
            res[site_hex]['bl_req_bw_meter'].append(node_to_push_bw)

    # Wrap up !
    if return_obj is True: return res
    return Response(
        json_util.dumps(res),
        mimetype='application/json'
    )

def fetch_xray_log(request):
    # Format string
    if not(request.json): return "NO JSON Post !", 400

    mydata = request.json 

    if not('xrayID' in mydata): return "Must specify xrayID", 400

    try:
        xrayID = str(mydata['xrayID'])
    except:
        return "xrayID should be a string !", 400

    # Connect to redis
    redis_client = utils.redis_utils.create_redis_client()

    res= []
    for node_log in redis_client.lrange('type=xraylog/xrayid=' + str(xrayID), 0, -1):
        node_to_push = json_util.loads(node_log)
        try:
            node_to_push['data'] = json_util.loads(node_to_push['data'])
        except:
            pass
        res.append(node_to_push)


    return Response(
        json_util.dumps(res),
        mimetype='application/json'
    )


def flush_all_redis():
    # Connect to redis and Reset the Redis !
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.flushall()

    return api_modules.utils.flask_response_json(True, {"msg" : "Redis flushed !"})


def flush_redis():
    # Connect to redis and Flush stats only !
    redis_client = utils.redis_utils.create_redis_client()
    
    # Flush by Log cluster
    for redis_family_keys in [  'type=xraylog/xrayid=*', 
                                'type=req_counter/config_id=*',
                                'type=req_bw_meter/config_id=*',
                                'type=bl_req_counter/config_id=*',
                                'type=bl_req_bw_meter/config_id=*',
                                'type=req_logger/config_id=*']:
        try:
            redis_client.eval('''return redis.call('del', unpack(redis.call('keys', ARGV[1])))''', 0, redis_family_keys)
        except:
            # LUA crashes when no keys found ;)
            pass


    return api_modules.utils.flask_response_json(True, {"msg" : "Stats flushed !"})