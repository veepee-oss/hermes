import json
import copy
import time
from operator import itemgetter
from threading import Thread

from bson import json_util
from flask import Response 


import api_modules.configs
import api_modules.logs
import api_modules.utils
import api_modules.sites
import utils.s3_utils

class Config_Fetcher(Thread):
    def __init__(self, config_id):
        Thread.__init__(self)
        self.config_id = config_id
        self.result = None

    
    def run(self):
        key_s3 = 'configs/config_id='+str(self.config_id)+'/conf.json'
        self.result = json.loads(utils.s3_utils.get_content(key_s3))




def summary(filtered_config_id = 0):
    consolidated_res = {} 
    # 1. Fetch configs 
    configs_fetched = []
    
    list_threads = []
    configs_available = api_modules.configs.list_configs(return_obj = True)
    for conf in configs_available:
        ay_thread = Config_Fetcher(conf['id'])
        ay_thread.start()
        list_threads.append(ay_thread)

    for ay_thread in list_threads:
        ay_thread.join()
        configs_fetched.append(copy.deepcopy({"id": ay_thread.config_id, "config": ay_thread.result}))


    # 2. Fetch Logs
    all_logs = api_modules.logs.fetch_all_logs(return_obj = True)

    # 3.1 Build the protocol table
    protocol_table = []
    for running_protocol in ['http','https','http2']:
        cte = 0
        cte_success = 0
        bw_meter = 0
        for config_id in list(all_logs.keys()):
            req_counter = all_logs[config_id]['req_counter']
            for node in req_counter:
                if node['protocol'] == running_protocol: 
                    cte = cte + node['reqs']
                    if (int(node['success']) == 1): cte_success = cte_success +  node['reqs']
            
            req_bw_meter = all_logs[config_id]['req_bw_meter']
            for node in req_bw_meter:
                if node['protocol'] == running_protocol: 
                    bw_meter = bw_meter + node['req_bw_bytes']
        
        if (cte > 0 ):
            success = str(int(round((float(cte_success) / float(cte)) * 100, 0))) + '%'
        else:
            success = '-'
        protocol_table.append({"protocol": running_protocol, "bandwidth": api_modules.utils._format_bw_string(bw_meter), "requests": api_modules.utils._format_requests_string(cte), "success": success})

    consolidated_res['stats_by_protocol'] = protocol_table

    # 3.2 Build the domain table
    ALL_cte = 0
    ALL_cte_success = 0
    ALL_bw_meter = 0

    unique_domains = {}
    for config_id in list(all_logs.keys()):
        req_counter = all_logs[config_id]['req_counter']
        for node in req_counter:
            if not node['domain'] in unique_domains:
                unique_domains[node['domain']] = {"cte": 0, "cte_success": 0, "bw_meter": 0}

            unique_domains[node['domain']]['cte'] += node['reqs']
            if (int(node['success']) == 1): unique_domains[node['domain']]['cte_success'] += node['reqs']

            ALL_cte += node['reqs']
            if (int(node['success']) == 1): ALL_cte_success += node['reqs']
        
        req_bw_meter = all_logs[config_id]['req_bw_meter']
        for node in req_bw_meter:
            if not node['domain'] in unique_domains:
                unique_domains[node['domain']] = {"cte": 0, "cte_success": 0, "bw_meter": 0}

            unique_domains[node['domain']]['bw_meter'] += node['req_bw_bytes']

            ALL_bw_meter += node['req_bw_bytes']

    list_domains = []

    for domain_k in list(unique_domains.keys()):
        cte = unique_domains[domain_k]['cte']
        cte_success = unique_domains[domain_k]['cte_success']
        bw_meter = unique_domains[domain_k]['bw_meter']

        if (cte > 0 ):
            success = str(int(round((float(cte_success) / float(cte)) * 100, 0))) + '%'
        else:
            success = '-'

        list_domains.append({"domain": domain_k, "bandwidth": api_modules.utils._format_bw_string(bw_meter), "requests": api_modules.utils._format_requests_string(cte), "success": success})

    list_domains = sorted(list_domains, key=itemgetter('requests'), reverse=True)

    consolidated_res['stats_by_domain'] = list_domains[:10]


    # 3.3 Build Configs stats
    config_name_dictionnary = {}
    configs_stats_table = []
    for config_node in configs_fetched:
        config_id_main = str(config_node['id'])
        try:
            config_name = config_node['config']['config_name']
        except:
            # Should not happen
            config_name = "UNTITLED"

        config_name_dictionnary[config_id_main] = config_name
        
        try:
            if 'js_mode' in config_node['config']['proxy']:
                if config_node['config']['proxy']['js_mode']:
                    proxy_name = 'JS function !'
                else:
                    proxy_name = config_node['config']['proxy']['host']
            else:
                proxy_name = config_node['config']['proxy']['host']
        except:
            # Should not happen
            proxy_name = "null"

        cte = 0
        cte_success = 0
        bw_meter = 0

        for config_id in list(all_logs.keys()):
            if str(config_id) == str(config_id_main):
                req_counter = all_logs[config_id]['req_counter']
                for node in req_counter:
                    cte = cte + node['reqs']
                    if (int(node['success']) == 1): cte_success = cte_success + node['reqs']
                
                req_bw_meter = all_logs[config_id]['req_bw_meter']
                for node in req_bw_meter:
                    bw_meter = bw_meter + node['req_bw_bytes']
        
        if (cte > 0 ):
            success = str(int(round((float(cte_success) / float(cte)) * 100, 0))) + '%'
        else:
            success = '-'


        configs_stats_table.append({"id": str(config_id_main), "proxy": proxy_name, "name": config_name, "bandwidth": api_modules.utils._format_bw_string(bw_meter), "requests": api_modules.utils._format_requests_string(cte), "success": success})
    
    consolidated_res['configs_stats'] = configs_stats_table

    # 3.4 Last requests logger
    all_request_list = []
    for config_id in list(all_logs.keys()):
        if (int(filtered_config_id) != 0): # we will filter
            if (int(filtered_config_id) != int(config_id)): continue #trim !

        req_logger = all_logs[config_id]['req_logger']
        for node in req_logger:
            try:
                path_i = node['req_data']['request_uri']['__DETAIL_path']
            except:
                path_i = "n.a."

            try:
                status_code = str(node['status_code'])
            except:
                status_code = "n.a."

            try:
                start_req_time = str(node['start_req_time'])
            except:
                start_req_time = "0000-00-00"


            try:
                req_duration_ms = str(node['req_duration_ms'])
            except:
                req_duration_ms = "n.a."

            try:
                internet_req_duration_ms = str(node['internet_req_duration_ms'])
            except:
                internet_req_duration_ms = "n.a."

            try:
                bandwidth = api_modules.utils._format_bw_string(node['bandwidth_b'])
            except:
                bandwidth = 'n.a.'
            
            
            try:
                TRIM_SIZE = 1000
                reply_str = str(node['reply'])
                trimmed_reply = reply_str[:TRIM_SIZE]
                if len(trimmed_reply) == TRIM_SIZE: 
                    trimmed_reply = trimmed_reply + ' ... (trimmed)'
            except:
                trimmed_reply = 'n.a.'

            all_request_list.append({"domain": node['domain'], "url": path_i, "config": str(config_id), "protocol": node['protocol'], "status": status_code, "bandwidth": bandwidth, "time": req_duration_ms, "time_internet": internet_req_duration_ms, "date": start_req_time, "config_name": config_name_dictionnary[str(config_id)], "details_node": {"req_data": node['req_data'], "req_connect": node['req_connect'], "reply": trimmed_reply}})

    all_request_list = sorted(all_request_list, key=itemgetter('date'), reverse=True)
    consolidated_res['req_logger'] = all_request_list[:100]

    # 3.5 All KPIs
    if (ALL_cte > 0 ):
        ALL_success = str(int(round((float(ALL_cte_success) / float(ALL_cte)) * 100, 0))) + '%'
    else:
        ALL_success = '-'

    consolidated_res['global_kpis'] = {"bandwidth": api_modules.utils._format_bw_string(ALL_bw_meter), "requests": api_modules.utils._format_requests_string(ALL_cte), "success": ALL_success, "configs": len(configs_available)}

    # 3.6 sites
    all_site_logs = api_modules.logs.fetch_bl_logs(return_obj = True)

    # 3.6.1 Aggreg by site
    res_sites_aggreg = []
    for site_hex in list(all_site_logs.keys()):
        cte = 0
        cte_success = 0
        bw_meter = 0

        for node in all_site_logs[site_hex]['bl_req_counter']:
            cte = cte + node['reqs']
            if (int(node['success']) == 1): cte_success = cte_success + node['reqs']

        for node in all_site_logs[site_hex]['bl_req_bw_meter']:
            bw_meter = bw_meter + node['req_bw_bytes']

        node_to_push_hex = {"created_at": all_site_logs[site_hex]['created_at'], "site_hex": site_hex, "regex": all_site_logs[site_hex]['regex']}

        if (cte > 0 ):
            bl_rate_float = 100 - int(round((float(cte_success) / float(cte)) * 100, 0))
            bl_rate = str(bl_rate_float) + '%'
        else:
            bl_rate_float = 0
            bl_rate = '-'


        node_to_push_hex["bandwidth"] =  api_modules.utils._format_bw_string(bw_meter)
        node_to_push_hex["requests"] = api_modules.utils._format_requests_string(cte)

        node_to_push_hex['bl_rate'] = bl_rate
        node_to_push_hex['bl_rate_float'] = bl_rate_float
        
        res_sites_aggreg.append(node_to_push_hex)

    res_sites_aggreg = sorted(res_sites_aggreg, key=itemgetter('created_at'), reverse=True)
    consolidated_res['sites'] = res_sites_aggreg

    # 3.6.1 Aggreg by site x config
    res_sites_conf_aggreg = {}
    for site_hex in list(all_site_logs.keys()):
        if not site_hex in res_sites_conf_aggreg: res_sites_conf_aggreg[site_hex] = {}
        for node in all_site_logs[site_hex]['bl_req_counter']:
            config_id = node['config_id']
            if not str(config_id) in res_sites_conf_aggreg[site_hex]: 
                res_sites_conf_aggreg[site_hex][str(config_id)] = {}
                res_sites_conf_aggreg[site_hex][str(config_id)]['cte'] = 0
                res_sites_conf_aggreg[site_hex][str(config_id)]['cte_success'] = 0
                res_sites_conf_aggreg[site_hex][str(config_id)]['bw_meter'] = 0

            res_sites_conf_aggreg[site_hex][str(config_id)]['cte'] += node['reqs']
            if (int(node['success']) == 1): res_sites_conf_aggreg[site_hex][str(config_id)]['cte_success'] += node['reqs']

        for node in all_site_logs[site_hex]['bl_req_bw_meter']:
            res_sites_conf_aggreg[site_hex][str(config_id)]['bw_meter'] += node['req_bw_bytes']

    res_sites_conf_aggreg_list = []
    for site_hex in list(res_sites_conf_aggreg.keys()):
        for config_id in list(res_sites_conf_aggreg[site_hex].keys()):
            node_to_push = copy.deepcopy(res_sites_conf_aggreg[site_hex][config_id])
            node_to_push['config_id'] = int(config_id)
            node_to_push['site_hex'] = site_hex

            if (res_sites_conf_aggreg[site_hex][config_id]['cte'] > 0 ):
                bl_rate_float = 100 - int(round((float(res_sites_conf_aggreg[site_hex][config_id]['cte_success']) / float(res_sites_conf_aggreg[site_hex][config_id]['cte'])) * 100, 0))
                bl_rate = str(bl_rate_float) + '%'
            else:
                bl_rate_float = 0
                bl_rate = '-'

            node_to_push['bl_rate'] = bl_rate
            node_to_push['bl_rate_float'] = bl_rate_float

            node_to_push["bandwidth"] =  api_modules.utils._format_bw_string(node_to_push["bw_meter"])
            node_to_push["requests"] = api_modules.utils._format_requests_string(node_to_push["cte"])

            node_to_push['regex'] = api_modules.sites.decode_name(site_hex)

            node_to_push['config_name'] = config_name_dictionnary[str(node_to_push['config_id'])]

            res_sites_conf_aggreg_list.append(node_to_push)

    res_sites_conf_aggreg_list = sorted(res_sites_conf_aggreg_list, key=itemgetter('bl_rate_float'), reverse=True)
    consolidated_res['sites_cross_confs'] = res_sites_conf_aggreg_list

    return Response(
        json_util.dumps(consolidated_res),
        mimetype='application/json'
    )
    