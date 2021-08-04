import requests
import random
import time
import gzip

import utils.config_handler
import api_modules.utils

def test_curl(request):
    if not(request.json): return "NO JSON Post !", 400
    mydata = request.json 
    
    if not('url' in mydata): return "Must specify url", 400
    
    if not('method' in mydata): return "Must specify method", 400
    if not mydata['method'] in ['POST','GET']: return "Supports GET & POST methods only", 400

    if not('headers' in mydata): return "Must specify headers", 400
    if not('data' in mydata): return "Must specify data", 400

    if not('config_id' in mydata): return "Must specify config_id", 400

    try:
        TIMEOUT = int(mydata['timeout'])
    except:
        TIMEOUT = 60

    try:
        config_id = int(mydata['config_id'])
    except:
        return "Must specify a valid config_id", 400


    SERVER_CONFIG = utils.config_handler.load_json_config()

    # ----- Create RayTracing token
    xray_token = str(random.randint(0,10000000000000)) + '_' + str(int(time.time()))

    # ----- Proxy
    proxy_url_auth = "http://"+SERVER_CONFIG['secrets']['proxy_username']+'-'+str(mydata['config_id'])+':'+SERVER_CONFIG['secrets']['proxy_password']+"@"+SERVER_CONFIG['mitm_configs']['host']+":"+ str(SERVER_CONFIG['mitm_configs']['port'])
    

    proxyDict = {
        "http"  : proxy_url_auth, 
        "https"  : proxy_url_auth, 
    }

    # ----- Headers
    headers_built = {}
    for (k,v) in mydata['headers']:
        headers_built[k] = v

    headers_built['xRayTrackingID'] = xray_token

    try:
        if (mydata['method'] =='GET'): r = requests.get(mydata['url'], headers=headers_built, timeout= int(TIMEOUT), data = mydata['data'], proxies=proxyDict, verify=False, stream=True)

        if (mydata['method'] =='POST'): r = requests.post(mydata['url'], headers=headers_built, timeout= int(TIMEOUT), data = mydata['data'], proxies=proxyDict, verify=False, stream=True)

        raw_response_captured =  r.raw.read()

        try:
            text_reponse = raw_response_captured.decode("utf-8")
        except:
            # Need decompression before !
            text_reponse = gzip.decompress(raw_response_captured).decode("utf-8")
        
        return api_modules.utils.flask_response_json(True, {"response": text_reponse, "xray_token": xray_token})
    except Exception as e:
        return api_modules.utils.flask_response_json(False, {"response": str(e), "xray_token": xray_token})