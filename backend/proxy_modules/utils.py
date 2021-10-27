import os
import copy
import base64

from http.server import BaseHTTPRequestHandler
from OpenSSL import crypto
from io import BytesIO
from socket import gethostname

import utils.config_handler


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    def get_header_val(self, header_key):
        for (k, v) in self.headers.items():
            if k.lower() == header_key.lower(): return v
        return None


class RSA:
    def __init__(self, dir=None):
        # Pubkey
        self.private_key_obj = crypto.PKey()
        self.private_key_obj.generate_key(crypto.TYPE_RSA, 2048)

        # Certificate info.
        self.certificate_obj = crypto.X509()
        self.certificate_obj.get_subject().C = "FR"
        self.certificate_obj.get_subject().ST = "Paris"
        self.certificate_obj.get_subject().L = "Paris"
        self.certificate_obj.get_subject().O = "Hermes"
        self.certificate_obj.get_subject().OU = "Hermes"
        self.certificate_obj.get_subject().CN = gethostname()
        self.certificate_obj.set_serial_number(1000)
        self.certificate_obj.gmtime_adj_notBefore(0)
        self.certificate_obj.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)

        # Setting certificate/privkey.
        self.certificate_obj.set_issuer(self.certificate_obj.get_subject())
        self.certificate_obj.set_pubkey(self.private_key_obj)
        self.certificate_obj.sign(self.private_key_obj, "sha1")

        # .crt and .key file dump.
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, self.certificate_obj)
        privkey = crypto.dump_privatekey(crypto.FILETYPE_PEM, self.private_key_obj)

        # Saves to "memory file."
        self.certificate = BytesIO(cert)
        self.private_key = BytesIO(privkey)

        # If dir is not passed, saves the certificate in /tmp/.
        if dir:
            self.save(dir)
        else:
            self.save("/tmp/mitm/")

    def save(self, dir):

        if not os.path.exists(dir):
            os.makedirs(dir)

        self.certificate_file = dir + "/mitm.crt"
        self.private_key_file = dir + "/mitm.key"

        with open(self.certificate_file, "wb") as f:
            f.write(self.certificate.getbuffer())

        with open(self.private_key_file, "wb") as f:
            f.write(self.private_key.getbuffer())


def fetch_config_and_auth(data, self_obj):
    Authorization_header = None

    if "connect_statement" in self_obj.__dict__:
        Authorization_header = HTTPRequest(self_obj.connect_statement).get_header_val('Proxy-Authorization')
        if Authorization_header is None: Authorization_header = HTTPRequest(self_obj.connect_statement).get_header_val('MITM-Proxy-Authorization')

    if Authorization_header is None:
        Authorization_header = HTTPRequest(data).get_header_val('Proxy-Authorization')
        if Authorization_header is None: Authorization_header = HTTPRequest(data).get_header_val('MITM-Proxy-Authorization')

    if Authorization_header is None: return False, None, "Not able to fetch creds for Proxy !"

    Authorization_header = Authorization_header.replace('Basic ', '')

    try:
        Authorization_header = base64.b64decode(Authorization_header).decode()

        username_config = Authorization_header.split(':')[0]
        password = Authorization_header.split(':')[1]

        username = username_config.split('-')[0]
        config_id = int(username_config.split('-')[1])

        SERVER_SECRETS = utils.config_handler.load_json_config()['secrets']

        if (username == SERVER_SECRETS['proxy_username']) and (password == SERVER_SECRETS['proxy_password']):
            return True, config_id, 'OK !'
        else:
            return False, None, "Incorrect proxy credentials !"
    except:
        return False, None, "Error during Username Config id Password parsing !"


def build_proxy_header_httpx(proxy, auth):
    if proxy is None: return None
    if auth is None:
        return {
                'http://': 'http://' + str(proxy[0]) +':' + str(proxy[1]),
                'https://': 'http://' + str(proxy[0]) +':' + str(proxy[1]),
            }
    else:
        return {
                'http://': 'http://' + auth[0]+':' + str(auth[1]) +'@' +str(proxy[0]) +':' + str(proxy[1]),
                'https://': 'http://' + auth[0]+':' + str(auth[1]) +'@' +str(proxy[0]) +':' + str(proxy[1]),
            }

def build_socks_conn_httpx(proxy, auth, type):
    if proxy is None: return None
    if auth is None:
        return str(type)+'://' + str(proxy[0]) +':' + str(proxy[1])
    else:
        return str(type)+'://' + str(auth[0])+':' + str(auth[1]) +'@' +str(proxy[0]) +':' + str(proxy[1])

def explode_request(input_request):
    if input_request is None: return None

    # This is a raw request: 
    # b'POST /fetch_data/get_products HTTP/1.1\r\nHost: scrap-v2.daco.io\r\nUser-Agent: curl/7.58.0\r\nAccept: */*\r\nAuthorization: Basic xxx==\r\nContent-Type: application/json\r\ncache-control: no-cache\r\nContent-Length: 30\r\n\r\n{\n    "ids": [273356598, 10]\n}'
    # Will become (pseudo json):
    # Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
    
    """
    {
        "request_uri":{
            "__CONSO__" : b'POST /fetch_data/get_products HTTP/1.1\r\n',
            "__DETAIL_command" : "POST",
            "__DETAIL_path:" : "/fetch_data/get_products",
            "__DETAIL_request_version" : "HTTP/1.1"
        },

        "headers": [
            ('User-Agent', 'curl/7.58.0'), 
            ('Accept', '*/*'), 
            ('Authorization', 'Basic xxx=='), 
            ('Content-Type', 'application/json'), 
            ('cache-control', 'no-cache'), 
            ('Content-Length', '30')
        ],

        "host": "scrap-v2.daco.io",

        "data": b'{\n    "ids": [273356598, 10]\n}'
    }
    """

    parsed_obj = HTTPRequest(input_request)

    # Handle Connection close
    trimmed_req = input_request.replace(b' ',b'').lower()
    trimmed_req = trimmed_req.split(b'\r\n\r\n')[0]
    
    connection_header = False
    connection_val = None
    
    if b'connection:keep-alive' in trimmed_req: 
        connection_header = True
        connection_val = 'keep-alive'

    if b'connection:close' in trimmed_req: 
        connection_header = True
        connection_val = 'close'

    new_headers = []
    host_isolated = None
    for (k,v) in parsed_obj.headers.items():
        if (k.lower() == 'connection'): continue
        if (k.lower() == 'host'): 
            host_isolated = copy.deepcopy(v)
            continue
        new_headers.append((k,v))

    # We isolate two specific headers : Host and Connection

    return {
        "request_uri" : {
            "__CONSO__": parsed_obj.raw_requestline,                        #eg: b'POST /fetch_data/get_products HTTP/1.1\r\n'
            
            "__DETAIL_command": parsed_obj.command,                         #eg: POST
            "__DETAIL_path": parsed_obj.path,                               #eg: /fetch_data/get_products
            "__DETAIL_request_version": parsed_obj.request_version          #eg: HTTP/1.1
        },
        
        "connection": {
            "present" : connection_header,                                  #eg: True
            "value_when_present": connection_val                            #eg: close
        },

        "headers": new_headers,                                             #eg: list [('Authorization', 'Basic xxx=='), ..., ('Content-Length','30')]
        "host": host_isolated,                                              #eg: scrap-v2.daco.io

        "data": parsed_obj.rfile.read()                                     #eg: b'{\n    "ids": [273356598, 10]\n}'
    } 

def _is_camel_capital(xPlodedReq):
    res = True #by default
    for (k,v) in xPlodedReq['headers']: 
        if k.lower() == k: return False
    return True

def _respect_camel_capital(input_key, is_camel):
    if is_camel is True:
        return input_key.title()
    else:
        return input_key.lower()

def implode_request(request_payload_input, re_compute_length = False):
    if request_payload_input is None: return None
    request_payload = copy.deepcopy(request_payload_input)

    # ----------------
    # ------- Command + Path
    raw_requestline = request_payload['request_uri']['__DETAIL_command'] + " " 
    raw_requestline = raw_requestline + request_payload['request_uri']['__DETAIL_path'] + " " 
    raw_requestline = raw_requestline + request_payload['request_uri']['__DETAIL_request_version'] + "\r\n" 
    
    # ----------------
    # ------- Headers

    # Camel capital
    camel_capital = _is_camel_capital(request_payload)

    # Content-Length
    if re_compute_length is True:
        headers_list_used = []
        for (k,v) in request_payload['headers']:
            if k.lower() != 'Content-Length'.lower():
                # Skip content length
                headers_list_used.append((k,v))
        headers_list_used.append((_respect_camel_capital('content-length', camel_capital), str(len(request_payload['data']))))
    else:
        headers_list_used = request_payload['headers']
    
    # Connection
    if (request_payload['connection']['present'] is True):
        # Added at the end
        headers_list_used.append((_respect_camel_capital('connection', camel_capital), request_payload['connection']['value_when_present']))
    
    # Host
    if not request_payload['host'] is None:
        # Added at the beginning
        headers_list_used = [(_respect_camel_capital('host', camel_capital), request_payload['host'])]+ headers_list_used

    # Build headers
    raw_requestline = raw_requestline + '\r\n'.join('%s: %s' % (k, v) for (k, v) in headers_list_used) + '\r\n\r\n'

    # Encode
    raw_requestline = raw_requestline.encode('utf-8')
    
    # ----------------
    # ------- Data
    raw_requestline = raw_requestline + request_payload['data']

    return raw_requestline



def kill_header_from_xploded_req(xPlodedReq, header_key):
    if xPlodedReq is None: return None

    res = copy.deepcopy(xPlodedReq)
    
    new_headers = []
    for (k,v) in xPlodedReq['headers']:
        if k.lower() != header_key.lower():
            new_headers.append((k,v))

    res['headers'] = new_headers

    return res


def get_header_from_xploded_req(xPlodedReq, header_key):
    if xPlodedReq is None: return None
    
    for (k,v) in xPlodedReq['headers']:
        if k.lower() == header_key.lower():
            return v

    return None

def merge_headers(xPlodedReq, headers_list_k_v):
    camel_capital = _is_camel_capital(xPlodedReq)
    res_xPlodedReq = copy.deepcopy(xPlodedReq)
    for node in headers_list_k_v:
        k = node[0]
        v = node[1]
        
        replaced_in_place = False
        for idx in range(len(res_xPlodedReq['headers'])):
            if res_xPlodedReq['headers'][idx][0].lower() == k.lower():
                res_xPlodedReq['headers'][idx] = (res_xPlodedReq['headers'][idx][0], v)
                replaced_in_place = True
        
        if replaced_in_place is False: 
            res_xPlodedReq['headers'].append((_respect_camel_capital(k,camel_capital), v))
            
    return res_xPlodedReq


def fetch_response_code(reply):
    if reply.count(b' ') < 2:
        raise IOError('Empty response')
    else:
        version, status, statusmsg = reply.split(b' ', 2)
        try:
            status = int(status)
            return status
        except ValueError:
            raise IOError('Malformed reponse')


def fetch_success_response(reply):
    try:
        status_code = fetch_response_code(reply)
        if status_code in [200, 301]:
            return 1
        else:
            return 0
    except Exception as e:
        return 0


def separate_header_and_body(reply):
    try:
        index = reply.index(b'\r\n\r\n')
    except:
        return (reply, bytes())
    else:
        index += len(b'\r\n\r\n')
        return (reply[:index], reply[index:])


def check_key_exists_non_null(input_dict, key_to_check):
    if key_to_check in input_dict:
        if input_dict[key_to_check] is None:
            return False
        else:
            if input_dict[key_to_check] == "":
                return False
            else:
                return True
    else:
        return False