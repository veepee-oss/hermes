import copy
import json
import ssl
import flexssl
import re
import base64
import subprocess
import os
import gzip
import random

from bson import json_util
from py_mini_racer import py_mini_racer

import utils.redis_utils
import proxy_modules.utils


def handle_connection_close_header(request_breakdown, json_config):
    try:
        do_not_modify_connection_header = json_config['do_not_modify_connection_header']
    except:
        do_not_modify_connection_header = False

    if do_not_modify_connection_header is False:
        # Default: means force connection close on request !
        new_req = copy.deepcopy(request_breakdown)
        new_req['connection'] = {"present": True, "value_when_present": "close"}
        return new_req
    else:
        # Do not modify ! keep it as is !
        return request_breakdown


def handle_request_headers(request_breakdown, json_config):
    try:
        headers_js_function = json_config['headers']
    except:
        headers_js_function = None

    if headers_js_function is None: return request_breakdown

    # Run the function !
    clean_function_code = headers_js_function.encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')
    clean_function_code_with_payload = clean_function_code.replace("DATA_ATTRIBUTE_INPUT",json.dumps(request_breakdown['headers']))

    ctx = py_mini_racer.MiniRacer()

    success = True
    try:
        function_output = json.loads(ctx.eval(clean_function_code_with_payload))
        new_headers = []
        for el in function_output:
            new_headers.append((el[0], el[1]))
    except Exception as e:
        success = False

    del ctx

    if success:
        new_req = copy.deepcopy(request_breakdown)
        new_req['headers'] = copy.deepcopy(new_headers)
        return new_req
    else:
        return request_breakdown


def _gen_key_freeze(node, config_id):
    list_headers = copy.deepcopy(node['headers'])
    list_headers = [str(x).lower() for x in list_headers]
    list_headers = sorted(list_headers)

    hashed_key = node['host_regex'].lower() + '-' + '-'.join(list_headers)
    hashed_key = base64.b64encode(hashed_key.encode('utf-8')).decode('ascii')
    return 'type=headers_freeze_data/config_id='+str(config_id)+'/key=' + hashed_key, 'type=headers_freeze_counter/config_id='+str(config_id)+'/key=' + hashed_key
    

def handle_request_headers_freeze(request_breakdown, json_config, config_id):
    # Init the context
    if not 'headers_freeze' in json_config: return request_breakdown, 'No actions taken'
    if request_breakdown['host'] is None: return request_breakdown, 'No actions taken'

    redis_client = utils.redis_utils.create_redis_client()

    request_breakdown_res = copy.deepcopy(request_breakdown)

    # Run the freeze
    return_msg_logs = []
    idx = -1
    for node in json_config['headers_freeze']:
        idx = idx + 1
        if re.search(node['host_regex'], request_breakdown_res['host']):
            # Check cached data
            key_data, key_counter = _gen_key_freeze(node, config_id)
            stored_val = redis_client.get(key_data)

            stored_counter = redis_client.get(key_counter)
            stored_counter = 0 if stored_counter is None else int(stored_counter)

            # Will cache if relevant
            if stored_val is None:
                will_cache = True
                data_to_freeze = []
                for header_i in node['headers']:
                    val_header = proxy_modules.utils.get_header_from_xploded_req(request_breakdown_res, header_i)
                    if val_header is None: 
                        will_cache = False
                    elif len(val_header) == 0:
                        will_cache = False
                    else:
                        data_to_freeze.append([header_i, val_header])
                
                if will_cache is True: 
                    redis_client.set(key_data, json_util.dumps(data_to_freeze))
                    redis_client.set(key_counter, 0)
                    return_msg_logs.append('Node idx ' + str(idx) + ': Stored values as headers present and no cached values')
                else:
                    return_msg_logs.append('Node idx ' + str(idx) + ': No actions taken ! No cached values and no headers present')
            
            # Will use cached headers
            else:
                redis_client.incr(key_counter)

                data_to_get = json_util.loads(stored_val)
                request_breakdown_res = proxy_modules.utils.merge_headers(request_breakdown_res, data_to_get) 

                # Respect max requests !
                if ((node['max_requests'] >= 0) and (stored_counter+1 >= node['max_requests'])): 
                    redis_client.delete(key_data)
                    redis_client.delete(key_counter)
                    return_msg_logs.append('Node idx ' + str(idx) + ': Used cached data and delete it as it reached maximum used times.')
                else:
                    return_msg_logs.append('Node idx ' + str(idx) + ': Used cached data !')
    
    return request_breakdown_res, '. '.join(return_msg_logs)


def handle_ssl_context(json_config):
    # ------------ Inputs fetch !

    # 1.1. Select the version
    try:
        version_ssl = json_config['ssl']['version']
    except:
        version_ssl = "PROTOCOL_TLS"

    # 1.2. Force SSL checks
    try:
        verify_ssl = json_config['ssl']['verify_ssl']
    except:
        verify_ssl = False

    # 1.3. Ciphers
    try:
        ciphers_ssl = json_config['ssl']['ciphers']
        if (ciphers_ssl == ""): ciphers_ssl = None
    except:
        ciphers_ssl = None

    # 1.4. Signatures (not used in HTTP2)
    try:
        signatures_ssl = json_config['ssl']['signatures']
        if (signatures_ssl == ""): signatures_ssl = None
    except:
        signatures_ssl = None



    used_version = ssl.PROTOCOL_TLS
    if (version_ssl == "PROTOCOL_TLS"): used_version = ssl.PROTOCOL_TLS
    if (version_ssl == "PROTOCOL_TLSv1"): used_version = ssl.PROTOCOL_TLSv1
    if (version_ssl == "PROTOCOL_TLSv1_1"): used_version = ssl.PROTOCOL_TLSv1_1
    if (version_ssl == "PROTOCOL_TLSv1_2"): used_version = ssl.PROTOCOL_TLSv1_2
    res_context = ssl.SSLContext(used_version) 

    
    if (verify_ssl is True):
        res_context.verify_mode = ssl.CERT_REQUIRED
    else:
        res_context.verify_mode = ssl.CERT_NONE

    if not ciphers_ssl is None: res_context.set_ciphers(ciphers_ssl)
    if not signatures_ssl is None: 
        flexssl.set_sigalgs(signatures_ssl, res_context)

    return res_context, {
        "version_ssl": version_ssl,
        "verify_ssl": verify_ssl,
        "ciphers_ssl": ciphers_ssl,
        "signatures_ssl": signatures_ssl
    }

def handle_http2_request(request_breakdown, json_config):
    try:
        http2 = json_config['http2']
    except:
        http2 = "NO"

    if not http2 in ['NO', 'YES', 'TRY']: http2 = "NO"

    if http2 == "NO": return False, {}

    if http2 == "TRY": return False, {}

    if http2 == "YES":
        host_to_req = request_breakdown['host']
        if host_to_req is None: return False, {}

        return True, {
            "headers": request_breakdown['headers'],
            "command": request_breakdown['request_uri']['__DETAIL_command'],
            "path": request_breakdown['request_uri']['__DETAIL_path'],
            "host_connect": "https://" + host_to_req,
            "data": request_breakdown['data'],
        }



def _delete_pass_file(file_name):
    try:
        os.remove(file_name)
    except:
        pass

def proxy_js_function(js_function_code):
    # Create the JS file
    file_tmp_to_run = "/tmp/js_proxy_node_" + str(random.randint(0,1000000000000000)) + '.js'
    _delete_pass_file(file_tmp_to_run)

    file_js_tmp = open(file_tmp_to_run,'w')
    file_js_tmp.write(js_function_code)
    file_js_tmp.close()

    # Run the JS and clean
    node_js_stdout = b""
    node_js_stderr = b""
    node_js_exec_err = ''
    data_carried = None
    try:
        node_running_process = subprocess.run(["node", file_tmp_to_run], capture_output=True)

        node_js_stdout = node_running_process.stdout
        node_js_stderr = node_running_process.stderr

        end_res = node_running_process.stdout
        # Formatting
        end_res = json.loads(end_res)

        proxy_host = end_res['host']

        if proxy_host is None:
            proxy_port = 0
        else:
            proxy_port = int(end_res['port'])

        if (not "type" in end_res): #HTTP by default not to break the existing config
            type=None
        else:
            type=end_res["type"]


        proxy_user = end_res['user']
        proxy_password = end_res['password']
        
        try:
            data_carried = end_res['data']
        except:
            pass
    except Exception as e:
        node_js_exec_err = str(e)
        end_res = None

    json_messages_js_run = {"stdout": node_js_stdout.decode('utf-8'), "stderr": node_js_stderr.decode('utf-8'), "execerr": node_js_exec_err, "data_carried" : data_carried}
        
    _delete_pass_file(file_tmp_to_run)

    # Return
    if end_res is None: return None, None, None,json_messages_js_run

    if proxy_host is None:
        json_messages_js_run['note'] = 'host is set to null'
        return None, None, None, json_messages_js_run  
    else:
        if (proxy_user is None) and (proxy_password is None): 
            json_messages_js_run['note'] = 'no authentication needed'
            return (proxy_host, proxy_port), None, type,json_messages_js_run
        else:
            return (proxy_host, proxy_port), (proxy_user, proxy_password), type,json_messages_js_run


def run_js_function_io(reply, proxy_verbose_messages, js_function_to_run, return_type = 'BINARY'):
    # return_type can be: 'BINARY' or None


    # Create the JS file
    random_pick = str(random.randint(0,1000000000000000))
    file_tmp_to_run = "/tmp/js_function_io_" + random_pick + '.js'
    _delete_pass_file(file_tmp_to_run)

    file_js_tmp = open(file_tmp_to_run,'w')
    file_js_tmp.write(js_function_to_run)
    file_js_tmp.close()

    # Build the Payload
    header, data = proxy_modules.utils.separate_header_and_body(reply)

    payload = {}
    payload['reply'] = {}
    try:
        payload['reply']["code"] = proxy_modules.utils.fetch_response_code(reply)
    except:
        payload['reply']["code"] = None
        
    try:
        payload['reply']['header'] = header.decode('utf-8')
    except:
        payload['reply']['header'] = None

    try:
        payload['reply']['data'] = gzip.decompress(data).decode('utf-8')
    except:
        try:
            payload['reply']['data'] = data.decode('utf-8')
        except:
            payload['reply']['data'] = None

    payload['proxy'] = proxy_verbose_messages
    
    file_tmp_to_load = "/tmp/js_function_io_" + random_pick + '.json'
    _delete_pass_file(file_tmp_to_load)

    file_js_tmp = open(file_tmp_to_load,'w')
    file_js_tmp.write(json.dumps(payload))
    file_js_tmp.close()
    
    # Run the JS and clean
    node_js_stdout = b""
    node_js_stderr = b""
    node_js_exec_err = ''

    try:
        node_running_process = subprocess.run(["node", file_tmp_to_run, file_tmp_to_load], capture_output=True)
        node_js_stdout = node_running_process.stdout
        node_js_stderr = node_running_process.stderr
    except Exception as e:
        node_js_exec_err = str(e)

    _delete_pass_file(file_tmp_to_run)
    _delete_pass_file(file_tmp_to_load)

    # Wrap up !
    if return_type == 'BINARY':
        if node_js_exec_err == '':
            try:
                end_res = int(node_running_process.stdout.decode('utf-8'))
            except Exception as e:
                node_js_exec_err = str(e)
                end_res = 0
        else:
            end_res = 0

        if not end_res in [0, 1]:
            end_res = 0
            node_js_exec_err = "Output should be 0 (not blacklisted) or 1 (blacklisted)"
        
        json_messages_js_run = {"stdout": node_js_stdout.decode('utf-8'), "stderr": node_js_stderr.decode('utf-8'), "execerr": node_js_exec_err}
        res = True if end_res == 1 else False,  json_messages_js_run
        return res
    
    if return_type is None:
        return {"stdout": node_js_stdout.decode('utf-8'), "stderr": node_js_stderr.decode('utf-8'), "execerr": node_js_exec_err}
