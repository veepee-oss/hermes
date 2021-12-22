import socket
import base64
import copy
import asyncio
import ssl
import h11
import socks
import uwsgi

import proxy_modules.utils
import proxy_modules.logging
import proxy_modules.transport
import proxy_modules.forgery

class EmulatedClient(object):
    def __init__(self, proxy = None, proxy_type = None, proxy_auth = None, timeout=30):
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.proxy_type = proxy_type

        socket.setdefaulttimeout(timeout)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.content_length = 0
        

    def _connect_socket_to_address(self, address, original_request, ReqxRayTrackingID):
        # Just connect to target !
        if self.proxy is None:
            self.sock.connect(address)
            return 200, {}

        if self.proxy_type in ["socks4", "socks5"]:
            proxy_addr, proxy_port = self.proxy
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2.0 Connecting to SOCKS Proxy', "SUCCESS", data = {})

            if(self.proxy_type == "socks4"):
                proxy_type = socks.SOCKS4
            else:
                proxy_type = socks.SOCKS5

            try:
                _hostname,_,ip_adresses = socket.gethostbyname_ex(address[0])
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2.0 DNS resolution done', "SUCCESS", data = {})
            except:
                 raise IOError('Step 2. ERROR : Cannot resolve domain name: ' + str(address[0]))

            try:
                self.sock = socks.create_connection(
                        (ip_adresses[0], address[1]),
                        proxy_type=proxy_type,
                        proxy_addr=proxy_addr,
                        proxy_port=proxy_port
                    )
                proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2.0 Connected to SOCKS Proxy', "SUCCESS", data = {})
            except:
                 raise IOError('Step 2. ERROR : Cannot connect to SOCKS proxy : ' + str(proxy_addr) +':'+str(proxy_port))
            
            return 200, {}
        
        else:
            # Will pass traffic to the Proxy !

            # Handle Proxy auth !
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2.0 Connecting to HTTP Proxy', "SUCCESS", data = {})
            
            headers = copy.deepcopy(proxy_modules.utils.HTTPRequest(original_request).headers)
            if not self.proxy_auth is None: headers['proxy-authorization'] = 'Basic ' + base64.b64encode(('%s:%s' % self.proxy_auth).encode('utf-8')).decode('utf-8')
            
            # Connect to Proxy
            self.sock.connect(self.proxy)
            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2.0 Connected to Proxy', "SUCCESS", data = {})


            try:
                http_version = original_request.decode("utf-8").split('\r\n')[0].split('HTTP/')[1]
            except:
                http_version = "1.1"
                
            # Transmit data
            fp = self.sock.makefile('w')
            fp.write('CONNECT %s:%d HTTP/%s\r\n' % (address[0],address[1],http_version))
            fp.write('\r\n'.join('%s: %s' % (k, v) for (k, v) in headers.items()) + '\r\n\r\n')
            fp.flush()
            
            # Fetch the Proxy response !
            fp = self.sock.makefile('r')
            statusline = fp.readline().rstrip('\r\n')

            if statusline.count(' ') < 2:
                fp.close()
                self.sock.close()
                try:
                    statusline_captured = str(statusline)
                except:
                    statusline_captured = 'MISSED'
                raise IOError('Step 2. ERROR : target CONNECT through Proxy failed ! Status line: ' + statusline_captured)

            proxy_modules.logging.log_xray(ReqxRayTrackingID, 'Step 2.0 Got a response from Target through proxy', "SUCCESS", data = {"response": statusline})
            
            version, status, statusmsg = statusline.split(' ', 2)
            if not version in ('HTTP/1.0', 'HTTP/1.1'):
                fp.close()
                self.sock.close()
                try:
                    version_captured = str(version)
                except:
                    version_captured = 'MISSED'
                raise IOError('Step 2. ERROR : Unsupported HTTP version ! Version: ' + version_captured)

            try:
                status = int(status)
            except ValueError:
                fp.close()
                self.sock.close()
                try:
                    status_captured = str(status)
                except:
                    status_captured = 'MISSED'
                raise IOError('Step 2. ERROR : Bad response Status ! Status: ' + status_captured)

            response_headers = {}

            while True:
                tl = ''
                l = fp.readline().rstrip('\r\n')
                if l == '':
                    break
                if not ':' in l:
                    continue
                k, v = l.split(':', 1)
                response_headers[k.strip().lower()] = v.strip()

            fp.close()
            
            return (status, response_headers)

    def sock_connect(self, data, ReqxRayTrackingID):
        path = proxy_modules.utils.HTTPRequest(data).headers["HOST"].split(":")
        try:
            port = int(path[1])
        except:
            port = 80
        self.server_address = (path[0], port)

        status, response_headers = self._connect_socket_to_address(self.server_address, data, ReqxRayTrackingID)
        

    def sock_connect_tls(self, connect, ssl_context_input, ReqxRayTrackingID):
        path = proxy_modules.utils.HTTPRequest(connect).path.split(":")
        self.server_address = (path[0], int(path[1]))

        status, response_headers = self._connect_socket_to_address(self.server_address, connect, ReqxRayTrackingID)
        self.sock = ssl_context_input.wrap_socket(self.sock, server_hostname=self.server_address[0])

    def sock_send(self, data):
        self.sock.send(data)

    def sock_close(self):
        self.sock.close()

    # --------------- Socket receive data -----------------
    # Source: https://gist.github.com/dsclose/bf0557e3e80ff7d66696

    def _init_buffer(self, buffer_size):
        buf = b''
        for p in range(buffer_size):
            buf += b' '
        return buf

    def read_until(self, condition, length_start=0, chunk_size=4096):
        data = bytes()
        chunk = bytes()
        length = length_start
        try:
            while not condition(length, chunk):
                chunk = self.sock.recv(chunk_size)

                if not chunk:
                    break
                else:
                    data += chunk
                    length += len(chunk)
        except socket.timeout:
            pass
        return data

    def end_of_header(self, length, data):
        # Returns true if data contains the end-of-header marker.
        return b'\r\n\r\n' in data

    def end_of_content(self, length, data):
        # Returns true if length does not fullfil the content_length.
        return self.content_length <= length

    def get_content_length(self, header):
        for line in header.split(b'\r\n'):
            if b'Content-Length:'.lower() in line.lower():
                return int(line[len(b'Content-Length:'):])
        return 0

    def sock_receive(self):
        data = self.read_until(self.end_of_header)
        header, body = proxy_modules.utils.separate_header_and_body(data)
        self.content_length = self.get_content_length(header)
        
        if (self.content_length > 0):
            body += self.read_until(self.end_of_content, len(body))
            return header + body
        else:
            # Fall back to waiting ...
            while True:
                try:
                    buf = self.sock.recv(4096)
                    if not buf:
                        break
                    else:
                        body += buf
                except Exception as e:
                    break
            return header + body
        

        """
        response = b""

        while True:
            try:
                buf = self.sock.recv(1024)
                if not buf:
                    break
                else:
                    response += buf
            except Exception as e:
                break
        return response
        """       

class ManInTheMiddle(object):
    def __init__(self, ca_public_key, ca_private_key):
        self.ca_public_key = ca_public_key
        self.ca_private_key = ca_private_key
        return

    async def handle_one_sock_request(self, reader, writer):
        protocol = proxy_modules.transport.Interceptor(self.ca_public_key,self.ca_private_key)
        protocol.connection_made(writer.transport)
        my_co = h11.Connection(h11.SERVER) #HTTP parser
        buffer_data = b''

        while True:
            try:
                data = await reader.read(1024)
            except:
                # Connection drop !
                data = b''

            buffer_data += data
            my_co.receive_data(data)
            event = my_co.next_event()

            if isinstance(event, h11.Request):
                # received plain http request ! Run the MITM
                await protocol.data_received(buffer_data)
                buffer_data = b''
            else:
                if buffer_data[:1] == b"\x16":
                    # Receiving encryted ssl tranfic !
                    await protocol.data_received(data)
                else:
                    # Receiving truncted http request, just buffer
                    pass
            
            if not data:
                # Connection closed
                break

    async def run_unique_server(self, idx): 
        server = await asyncio.start_server(    self.handle_one_sock_request, 
                                                sock = socket.fromfd(uwsgi.sockets[idx], socket.AF_INET, socket.SOCK_STREAM)
                                            )
        await server.serve_forever()

    async def run_all_servers(self):
        # Fetch all sockets
        idx = 0
        for fd in uwsgi.sockets:
            idx += 1

        # Pile them
        tasks = []
        for i in range(idx):
            task_i = asyncio.create_task(self.run_unique_server(i))
            tasks.append(task_i)

        # Await
        for task_i in tasks:
            await task_i

    #async def run_unique_server_no_uwsgi(self):  
    #    # use this function to avoid using uwsgi (debug)                 
    #    server = await asyncio.start_server(self.handle_one_sock_request,'0.0.0.0', 8080)
    #    await server.serve_forever()

    def run(self):
        #asyncio.run(self.run_unique_server_no_uwsgi())
        asyncio.run(self.run_all_servers())