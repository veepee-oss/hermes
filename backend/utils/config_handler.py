import os
import sys
import json

def load_json_config():
    Servers_Config = "config.json"
    if not(os.path.isfile(Servers_Config)): sys.exit("0 : Configuration file: "+Servers_Config + " not found !")
    with open(Servers_Config) as data_file:    
        Servers_Config_Dict = json.load(data_file)


    Servers_Config_Dict['redis_server'] = {}
    Servers_Config_Dict['redis_server']['host'] = os.environ['REDIS_URL']
    Servers_Config_Dict['redis_server']['port'] = os.environ['REDIS_PORT']

    Servers_Config_Dict['secrets'] = {}

    # ---- for API only
    try:
        Servers_Config_Dict['secrets']['secret_app'] = os.environ['SECRET_KEY_APP']
        Servers_Config_Dict['secrets']['api_username'] = os.environ['API_USERNAME']
        Servers_Config_Dict['secrets']['api_password'] = os.environ['API_PASSWORD']
    except:
        Servers_Config_Dict['secrets']['secret_app'] = None
        Servers_Config_Dict['secrets']['api_username'] = None
        Servers_Config_Dict['secrets']['api_password'] = None


    Servers_Config_Dict['mitm_configs'] = {}
    try:
        Servers_Config_Dict['mitm_configs']['host'] = os.environ['MITM_TEST_URL']
    except:
        Servers_Config_Dict['mitm_configs']['host'] = '127.0.0.1'

    try:
        Servers_Config_Dict['mitm_configs']['port'] = os.environ['MITM_TEST_PORT']
    except:
        Servers_Config_Dict['mitm_configs']['port'] = '8080'


    # ---- for MITM only
    try:
        Servers_Config_Dict['secrets']['proxy_username'] = os.environ['PROXY_USERNAME']
        Servers_Config_Dict['secrets']['proxy_password'] = os.environ['PROXY_PASSWORD']
    except:
        Servers_Config_Dict['secrets']['proxy_username'] = None
        Servers_Config_Dict['secrets']['proxy_password'] = None


    return Servers_Config_Dict
