import datetime
import json
from bson import json_util

import utils.redis_utils
import proxy_modules.utils

class color:
    reset = "\u001b[0m"

    @staticmethod
    def red(text):
        return "\033[1;31;40m" + str(text) + color.reset

    @staticmethod
    def green(text):
        return "\033[1;32;40m" + str(text) + color.reset

    @staticmethod
    def yellow(text):
        return "\033[1;33;40m" + str(text) + color.reset

def log_system_log(message, tag):
    # tag should be SUCCESS, INFO, ERROR, WARNING
    now = datetime.datetime.now()
    res = now.strftime("%Y-%m-%d %H:%M:%S")
    res = res + " [" + tag + "] " + message

    if tag == "SUCCESS": print(color.green(res))
    if tag == "ERROR": print(color.red(res))
    if tag == "WARNING": print(color.yellow(res))
    if tag == "INFO": print(res)

# ---------------------------------------------------
# ------------------ Logging Utils !------------------
# ---------------------------------------------------
def serialize_data(input_obj):
    try:
        return json.dumps(input_obj, indent=4, sort_keys=True, ensure_ascii=False, default=json_util.default)
    except Exception as e:
        return json.dumps({"error" : "could not serialize data, error : " + str(e)}, 
                            indent=4, sort_keys=True, ensure_ascii=False, default=json_util.default)

def de_serialize_data(input_string):
    try:
        return json_util.loads(input_string)
    except Exception as e:
        return {"error" : "could not de_serialize data, error : " + str(e)}

# ---------------------------------------------------
# ------------------ xRAY LOGGING !------------------
# ---------------------------------------------------
# -- Key format: 'type=xraylog/xrayid=' + str(xRayID)


def clear_log_xray(xRayID):
    if xRayID is None: return 
    key_redis = 'type=xraylog/xrayid=' + str(xRayID)

    redis_client = utils.redis_utils.create_redis_client()
    redis_client.delete(key_redis)
    return

def log_xray(xRayID, message, tag, data = None):
    # tag should be SUCCESS, INFO, ERROR, WARNING
    if xRayID is None: return
    key_redis = 'type=xraylog/xrayid=' + str(xRayID)

    # Prepare the request
    strigified_data = serialize_data(data)
    date_now_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_to_push = date_now_string+ " [XRAY: " + str(xRayID) + "] [" + tag + "] " + message
    
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.rpush(key_redis, json.dumps({"message": message_to_push, "date": date_now_string, "data": strigified_data, "tag": tag}))
    redis_client.expire(key_redis, 3600 * 24 * 7) #7 days !
    

# ---------------------------------------------------
# ------------------ Request counts -----------------
# ---------------------------------------------------
# -- Key format: 'type=req_counter/config_id=2/domain=www.google.fr/protocol=https/success=1
# -- Key format: 'type=req_bw_meter/config_id=2/domain=www.google.fr/protocol=http2/success=1

def request_count(config_id, domain, protocol, reply, force_fail = False):
    if force_fail is True:
        success = 0
        bw_add = 0
    else:
        try:
            bw_add = len(reply)
        except:
            bw_add = 0

        success = proxy_modules.utils.fetch_success_response(reply)

    key_counter = 'type=req_counter/config_id='+str(config_id)+'/domain='+str(domain)+'/protocol='+str(protocol)+'/success='+str(success)
    key_bw = 'type=req_bw_meter/config_id='+str(config_id)+'/domain='+str(domain)+'/protocol='+str(protocol)+'/success='+str(success)
    
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.incr(key_counter, amount = 1)
    redis_client.incr(key_bw, amount = bw_add)

    redis_client.expire(key_counter, 3600 * 24 * 7) #7 days !
    redis_client.expire(key_bw, 3600 * 24 * 7) #7 days !
    return


# ---------------------------------------------------
# ------------------ Blacklist  counts --------------
# ---------------------------------------------------
# -- Key format: 'type=bl_req_counter/config_id=2/site_hex=4C69706B59584A3065533471/success=1'
# -- Key format: 'type=bl_req_bw_meter/config_id=2/site_hex=4C69706B59584A3065533471/success=0'

def bl_request_count(config_id, site_hex, success, reply):
    try:
        bw_add = len(reply)
    except:
        bw_add = 0

    key_counter = 'type=bl_req_counter/config_id='+str(config_id)+'/site_hex='+str(site_hex)+'/success='+str(success)
    key_bw = 'type=bl_req_bw_meter/config_id='+str(config_id)+'/site_hex='+str(site_hex)+'/success='+str(success)
    redis_client = utils.redis_utils.create_redis_client()
    redis_client.incr(key_counter, amount = 1)
    redis_client.incr(key_bw, amount = bw_add)

    redis_client.expire(key_counter, 3600 * 24 * 7) #7 days !
    redis_client.expire(key_bw, 3600 * 24 * 7) #7 days !
    return

# ---------------------------------------------------
# ------------------ Request Logs (last 1000 ) ------
# ---------------------------------------------------
# -- Key format: 'type=req_logger/config_id=2

def trail_log_request(config_id, domain, protocol, req_data, req_connect, reply, start_req_time_obj, req_duration_ms, internet_req_duration_sec):
    key_counter = 'type=req_logger/config_id='+str(config_id)

    try:
        status_code = proxy_modules.utils.fetch_response_code(reply)
    except:
        status_code = None

    try:
        bw = len(reply)
    except:
        bw = 0


    # What to log ? Error ? or truncated reply ?
    truncate_reply = True
    if isinstance(reply, dict):
        if "error_node" in reply:
            if reply['error_node'] is True:
                truncate_reply = False
    
    if truncate_reply is False:
        truncated_reply = reply
    else:
        try:
            truncated_reply = reply[:1000] #To avoid heavy responses ...
        except:
            truncated_reply = b'Reply could not be truncated !'

    node_to_push = {
        "domain" : domain,
        "protocol" : protocol,
        "req_data": req_data,
        "bandwidth_b": bw,
        "req_connect": req_connect,
        "reply": truncated_reply,
        "status_code" : status_code,
        "start_req_time": start_req_time_obj,
        "internet_req_duration_ms": int(round(internet_req_duration_sec * 1000)),
        "req_duration_ms": int(round(req_duration_ms * 1000))
    }

    redis_client = utils.redis_utils.create_redis_client()
    redis_client.lpush(key_counter, json.dumps(node_to_push, indent=4, sort_keys=True, ensure_ascii=False, default=json_util.default))
    redis_client.ltrim(key_counter,  0, 999)
    redis_client.expire(key_counter, 3600 * 24 * 7) #7 days !