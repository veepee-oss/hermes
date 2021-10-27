import asyncio
import httpx
from httpx_socks import SyncProxyTransport

import ssl
import time
import datetime
import re

import sys
import os
import traceback

from threading import Thread

import proxy_modules.utils
import proxy_modules.backbone
import proxy_modules.logging
import proxy_modules.configs
import proxy_modules.forgery

class HTTP(asyncio.Protocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data_original):
        try:
            # ------------------------------------------------
            # -------- PART 0 : init
            # ------------------------------------------------
            requested_host = None
            requested_protocol = 'https'
            url_ressource_fetch = None
            config_id = None
            xPlodedReq = None
            xPlodedConnectReq = None
            ReqxRayTrackingID = None
            start_req_time = time.time()
            start_req_time_obj = datetime.datetime.now()
            internet_req_duration_sec = 0.0

            # ------------------------------------------------
            # -------- PART 1 : Check proxy creds and conf
            # ------------------------------------------------
            # data: contains the real request (GET, POST, ...)
            # self.connect_statement: contains the connect Request
            auth_check, config_id, auth_check_message = proxy_modules.utils.fetch_config_and_auth(data_original, self)
            
            if auth_check is False:
                self.transport.write(b"HTTP/1.1 407 Proxy Authentication Required\r\n\r\n")
                self.close()
                return 

            json_config = proxy_modules.configs.fetch_config_live_redis(config_id)

            if json_config is None:
                self.transport.write(b"HTTP/1.1 401 Unauthorized\r\n\r\n")
                self.close()
                return


            # ------------------------------------------------
            # -------- PART 1.1 : Connect / request cleaning
            # ------------------------------------------------ 
            xPlodedReq = proxy_modules.utils.explode_request(data_original)
            requested_host = xPlodedReq['host']

            if "connect_statement" in self.__dict__:
                xPlodedConnectReq = proxy_modules.utils.explode_request(self.connect_statement)
                requested_protocol = 'https'
            else:
                xPlodedConnectReq = None
                requested_protocol = 'http'

            if not xPlodedReq['host'] is None: url_ressource_fetch = requested_protocol + '://' + xPlodedReq['host'] + xPlodedReq['request_uri']['__DETAIL_path']

            # // Clean Proxy headers : consumed already !
            ReqxRayTrackingID = proxy_modules.utils.get_header_from_xploded_req(xPlodedReq, 'xRayTrackingID')
            proxy_modules.logging.clear_log_xray(ReqxRayTrackingID)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.1. Initiating xRay tracing for this request !', "INFO", data = {})

            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.1. Displaying original requests', "INFO", data = {"data": xPlodedReq, "connect_req": xPlodedConnectReq})

            for header_to_clean in ['Proxy-Authorization', 'xRayTrackingID', 'MITM-Proxy-Authorization']:
                xPlodedReq = proxy_modules.utils.kill_header_from_xploded_req(xPlodedReq, header_to_clean)
                xPlodedConnectReq = proxy_modules.utils.kill_header_from_xploded_req(xPlodedConnectReq, header_to_clean)
            
            if not xPlodedConnectReq is None:
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.1. CONNECT request placed', "INFO", data = {})
            
            # ------------------------------------------------
            # -------- PART 1.15 : Blacklist check
            # ------------------------------------------------
            if not xPlodedReq['host'] is None:
                if 'blacklist' in json_config:
                    for bl_i in json_config['blacklist']:
                        if re.search(bl_i, url_ressource_fetch):
                            # Blacklisted !
                            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.15. Request URL blacklisted by Config !', "INFO", data = {"urlFetched": url_ressource_fetch, "blacklistRegex": bl_i})
                            
                            # Logging !
                            proxy_modules.logging.request_count(config_id, requested_host, requested_protocol, None, force_fail = True)
                            proxy_modules.logging.trail_log_request(config_id, requested_host, requested_protocol, xPlodedReq, xPlodedConnectReq, {"error": "Blacklisted", 'error_node': True}, start_req_time_obj, time.time() - start_req_time, internet_req_duration_sec)  

                            self.transport.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
                            self.close()
                            return

            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.15. No Blacklist on this URL', "INFO", data = {})
            
            # ------------------------------------------------
            # -------- PART 1.2 : PROXY CONFIG !
            # ------------------------------------------------
            config_proxy_node, config_proxy_auth_node, config_proxy_type_node, proxy_verbose_messages = proxy_modules.configs.extract_proxy_config(json_config)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.2. Extracted proxy params.', "INFO", data = {"config_proxy_node": config_proxy_node, "config_proxy_auth_node" : "hidden", "log": proxy_verbose_messages,"config_proxy_type_node":config_proxy_type_node})

            # ------------------------------------------------
            # -------- PART 1.25 : Headers Freeze
            # ------------------------------------------------
            xPlodedReq, extensive_logs = proxy_modules.forgery.handle_request_headers_freeze(xPlodedReq, json_config, config_id)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.25. Headers freeze handled.', "INFO", data = {"data" : xPlodedReq, "detailed_logs": extensive_logs})

            # ------------------------------------------------
            # -------- PART 1.3 : Headers management
            # ------------------------------------------------
            xPlodedReq = proxy_modules.forgery.handle_request_headers(xPlodedReq, json_config)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.3. Headers management handled.', "INFO", data = xPlodedReq)

            # ------------------------------------------------
            # -------- PART 1.4 : CONNECTION Flag !
            # ------------------------------------------------
            xPlodedReq = proxy_modules.forgery.handle_connection_close_header(xPlodedReq, json_config)
            if not xPlodedConnectReq is None: xPlodedConnectReq = proxy_modules.forgery.handle_connection_close_header(xPlodedConnectReq, json_config)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.4. Connection flag handled.', "INFO", data = {"data": xPlodedReq, "connect_req": xPlodedConnectReq})

            # ------------------------------------------------
            # -------- PART 1.5 : HTTP2
            # ------------------------------------------------
            use_http_2, http2_req = proxy_modules.forgery.handle_http2_request(xPlodedReq, json_config)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.5. HTTP2 handled.', "INFO", data = {"use_http_2": use_http_2, "http2_req": http2_req})

            # ------------------------------------------------
            # -------- PART 1.6 : SSL Params !
            # ------------------------------------------------
            ssl_context_used, meta_data_ssl = proxy_modules.forgery.handle_ssl_context(json_config)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.6. SSL Params handled.', "INFO", data = meta_data_ssl)

            # ------------------------------------------------
            # -------- PART 1.7 : Check Site hit !
            # ------------------------------------------------
            site_hit, site_regex, site_hex, site_bl_func = proxy_modules.configs.fetch_site_match_redis(url_ressource_fetch)
            if site_hit is False:
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.7. Site not found !', "INFO", data = {"uri": url_ressource_fetch})
            else:
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 1.7. Site found !', "INFO", data = {"uri": url_ressource_fetch, "regex": site_regex})

            
            # ------------------------------------------------
            # -------- PART 2 : Send the Request to Target 
            # ------------------------------------------------            
            
            if use_http_2 is False:
                # Compile HTTP 1.x request:
                data = proxy_modules.utils.implode_request(xPlodedReq)
                connect_req = proxy_modules.utils.implode_request(xPlodedConnectReq)
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2. Running HTTP1.x request, connecting socket ...', "INFO", data = {"data": xPlodedReq, "connect_req": xPlodedConnectReq})

                # Creates emulated client.
                emulated_client = proxy_modules.backbone.EmulatedClient(proxy = config_proxy_node, proxy_auth = config_proxy_auth_node, proxy_type=config_proxy_type_node)
                
                time_marker = time.time()

                # Checks if we are in the HTTP or HTTPS class.
                if not connect_req is None:
                    # HTTPS
                    emulated_client.sock_connect_tls(connect_req, ssl_context_used, ReqxRayTrackingID)
                else:
                    # HTTP
                    emulated_client.sock_connect(data, ReqxRayTrackingID)
                

                # Sends the data to the server.
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2. Socket connected, sending data ...', "SUCCESS", data = {})
                emulated_client.sock_send(data)
                
                # Receives the reply and responds back to client.
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2. Data sent, receiving data ...', "INFO", data = {})
                reply = emulated_client.sock_receive()
                # Done internet request !
                internet_req_duration_sec += time.time() - time_marker
            else:
                requested_protocol = 'http2'
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2. Running HTTP2.0 request ...', "INFO", data = {})
                HTTP2_req_obj = HTTP2(http2_req, ssl_context_used, config_proxy_node, config_proxy_auth_node,config_proxy_type_node)
                
                # Perform the HTTP 2 request!
                time_marker = time.time()
                reply = HTTP2_req_obj.fetch_ressource()

                # Done internet request !
                internet_req_duration_sec += time.time() - time_marker
            
            # ------------------------------------------------
            # -------- PART 3 : Handle response 
            # ------------------------------------------------ 
            if site_hit is True:
                bl_input_node_code_proxy = {"host": config_proxy_node, "auth": config_proxy_auth_node, "log": proxy_verbose_messages,"type":config_proxy_type_node}
                am_i_blacklisted, json_verbose_msg = proxy_modules.forgery.run_js_function_io(reply, bl_input_node_code_proxy , site_bl_func, return_type = 'BINARY')
                
                proxy_modules.logging.bl_request_count(config_id, site_hex, 1 if am_i_blacklisted is False else 0, reply)
                
                if am_i_blacklisted is True:
                    if proxy_modules.utils.check_key_exists_non_null(json_config, 'site_blacklist_response') is True:
                        proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 3.1 I have been blacklisted ! I will respond accordingly !', "WARNING", data = json_verbose_msg)

                        response_log_bl_response = proxy_modules.forgery.run_js_function_io(reply, bl_input_node_code_proxy, json_config['site_blacklist_response'], return_type = None)

                        proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 3.2 Responded to blacklist !', "INFO", data = response_log_bl_response)

                    else:
                        proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 3. I have been blacklisted ! No response defined in the config !', "WARNING", data = json_verbose_msg)
                else:
                    proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 3. I am not blacklisted ! Continuing ...', "SUCCESS", data = json_verbose_msg)
            else:
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 3. No Blacklist check done !', "INFO", data = {})

            # ------------------------------------------------
            # -------- PART 4 : Send the Final Response to Origin 
            # ------------------------------------------------
            # Send reply to client
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 4. Data received, sending data back to Client ...', "SUCCESS", data = {"reply": reply})
            self.transport.write(reply)
            
            # Closing the EmulatedClient socket.
            if use_http_2 is False:
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 4. Closing HTTP1.x target request socket...', "INFO", data = {})
                emulated_client.sock_close()

            # Closing connection with the client.
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 4. Closing client socket ...', "INFO", data = {})
            self.close()

            # Logging
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 4. Request done !', "SUCCESS", data = {})
            proxy_modules.logging.request_count(config_id, requested_host, requested_protocol, reply)
            proxy_modules.logging.trail_log_request(config_id, requested_host, requested_protocol, xPlodedReq, xPlodedConnectReq, reply, start_req_time_obj, time.time() - start_req_time, internet_req_duration_sec)

        except Exception as e:
            # Traceback complete error log
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error_message = "Code error captured in file: "+ fname +" in line: "+str(exc_tb.tb_lineno)+". Error message: " + str(e)+ '. All error: ' + traceback.format_exc()
            
            # Logging !
            proxy_modules.logging.request_count(config_id, requested_host, requested_protocol, None, force_fail = True)
            proxy_modules.logging.trail_log_request(config_id, requested_host, requested_protocol, xPlodedReq, xPlodedConnectReq, {"complete_error": error_message, "sharp_error": str(e), 'error_node': True}, start_req_time_obj, time.time() - start_req_time, internet_req_duration_sec)            
            if not ReqxRayTrackingID is None: proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Error during MITM', "ERROR", data = {"complete_error": error_message, "sharp_error": str(e)})
            proxy_modules.logging.log_system_log("Error during MITM : " + error_message, "ERROR")

            # Close transport
            self.close()

    def close(self):
        # Closes connection with the client.
        self.transport.close()

class HTTPS:
    def __new__(cls, ssl_context):
        # Returning our HTTPS transport.
        return asyncio.sslproto.SSLProtocol(
            loop=asyncio.get_running_loop(),
            app_protocol=HTTP(),
            sslcontext=ssl_context,
            waiter=None,
            server_side=True,
        )


class HTTP2(object):
    def __init__(self, http2_req, ssl_context_used, config_proxy_node, config_proxy_auth_node,config_proxy_type_node):
        self.http2_req = http2_req
        self.ssl_context_used = ssl_context_used
        self.config_proxy_node = config_proxy_node
        self.config_proxy_auth_node = config_proxy_auth_node
        self.config_proxy_type_node = config_proxy_type_node


    def fetch_ressource(self):
        # Make a HTTP2 request to the Target
        if(self.config_proxy_type_node in ["socks4","socks5"]):
            transport = SyncProxyTransport.from_url(proxy_modules.utils.build_socks_conn_httpx(self.config_proxy_node, self.config_proxy_auth_node,self.config_proxy_type_node))
            co2 = httpx.Client( base_url= self.http2_req['host_connect'], 
                                    headers = self.http2_req['headers'], 
                                    transport = transport, 
                                    http2 = True, 
                                    verify = self.ssl_context_used, 
                                    timeout = 60)
        else:
            co2 = httpx.Client( base_url= self.http2_req['host_connect'], 
                                    headers = self.http2_req['headers'], 
                                    proxies = proxy_modules.utils.build_proxy_header_httpx(self.config_proxy_node, self.config_proxy_auth_node), 
                                    http2 = True, 
                                    verify = self.ssl_context_used, 
                                    timeout = 60)
        

        request = co2.build_request(self.http2_req['command'],
                                    self.http2_req['path'],
                                    data = self.http2_req['data'])

        __http_response = co2.send(request)

        # Build a HTTP1.1 response for the Client
        __response_data =__http_response.read()
        __response_headers = __http_response.headers
        __code = __http_response.status_code
        __message =__http_response.reason_phrase

        final_response = 'HTTP/1.1 ' + str(__code)  + ' ' + __message + '\r\n'
        final_response = final_response + '\r\n'.join('%s: %s' % (k, v) for (k, v) in __response_headers.items()) + '\r\n\r\n'
        final_response = final_response.encode('utf-8')
        final_response = final_response + __response_data
        reply = final_response

        return reply


class http_processor(Thread):
    def __init__(self, http_obj, data):
        Thread.__init__(self)
        self.http_obj = http_obj
        self.data = data
        self.finished = False

    def run(self):
        try:
            self.http_obj.data_received(self.data)
            self.finished = True
        except Exception as e:
            self.finished = True
            raise(e)

class Interceptor(asyncio.Protocol):
    def __init__(self, ssl_context):
        # Initiating our HTTP/HTTPS protocols.
        self.HTTP = HTTP()
        self.HTTPS = HTTPS(ssl_context)

        # Creates the TLS flag. Will be used later.
        self.using_tls = False

    def connection_made(self, transport):
        # Setting our transport object.
        self.transport = transport

        # Getting the client address and port number.
        address, port = self.transport.get_extra_info("peername")

        # Prints opening client information.
        #print(f"CONNECTING WITH {address}:{port}")

    async def data_received(self, data):
        # Parses the data the client has sent to the server.
        request = proxy_modules.utils.HTTPRequest(data)

        # Decides where to send data to (HTTP or HTTPS protocol).
        if request.command == "CONNECT" and self.using_tls == False:
            
            # Replies to the client that the server has connected.
            self.transport.write(b"HTTP/1.1 200 OK\r\n\r\n")

            # Does a TLS/SSL handshake with the client.
            self.HTTPS.connection_made(self.transport)

            # Sets our TLS flag to true.
            self.using_tls = True

            # Sends the CONNECT to the HTTPS protocol for storage and print.
            # Since this is the initial 'CONNECT' data, it will be unencrypted.
            self.HTTPS._app_protocol.connect_statement = data

        elif self.using_tls:
            # With HTTPS protocol enabled, receives encrypted data from the client.
            self.HTTPS.data_received(data)

        else:
            # Receives standard, non-encrypted data from the client (TLS/SSL is off).
            self.HTTP.connection_made(self.transport)
            #self.HTTP.data_received(data)

            thread_processor = http_processor(self.HTTP, data)
            thread_processor.start()
            while thread_processor.finished is False:
                await asyncio.sleep(0.1)
