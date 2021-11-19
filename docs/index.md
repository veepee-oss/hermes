# Hermes MITM Proxy

Hermes is a **man-in-the-middle proxy** that allows HTTP, HTTPS and HTTP/2 trafic interception, inspection and modification. 

It can be used for application testing and debugging, privacy measurements, penetration testing and network monitoring.

# Table of contents

1. [Usage](#usage)
    1. [Hello World](#hello-world)
    2. [SSL](#ssl)
    3. [Authentification](#authentification)
2. [Configurations](#configurations)
    1. [JSON format](#json-format)
    2. [UI format](#ui-format)
3. [UI Testing](#ui-testing)
4. [Features](#features)
    1. [SSL handshake](#ssl-handshake)
    2. [HTTP2](#http2)
    3. [Proxy](#proxy)
        1. [Simple Proxy](#simple-proxy)
        2. [Advanced Proxy](#advanced-proxy)
    4. [Headers](#headers)
    5. [Headers Freeze](#headers-freeze)
    6. [Sites](#sites)
        1. [Sites config](#sites-config)
        2. [Sites reply](#sites-reply)

# Usage

This will assume you have all the services installed using the **docker-compose** method (see [README.md](../README.md)) and you have the following 3 services:

 - http://localhost: The web server for the UI
 - http://localhost:443/ : The REST API service
 - http://localhost:8080/ : The MITM service

We will be using the default credentials in the **docker-compose** file but you should modify them !

## Hello World

The docker install has already a vanilla / hello world config with id = 1.

You can run this command to test the MITM service:

```bash
$: curl -X GET \
    https://api.ipify.org?format=json \
    --proxy http://proxy_username-1:PVnkJazW2weJ6EcyZKgoZ7cNbckXVeGje4P@localhost:8080 \
    --insecure \
    -H 'Content-Type: application/json'
```

The output should display your public IP.


## SSL

Hermes creates a self-signed certificate to channel HTTPS and HTTP/2 requests.

You should use the **--insecure** flag for each of your requests or configure your Internet browser to bypass this restriction.

But, you can **force Hermes to use your own certificate**, you should then place the cert and key files in these locations:


    /etc/ssl/private/mitm.crt
    /etc/ssl/private/mitm.key

Then add this certificate to your list of **approved certificates** by the OS.

### Add a self-signed certificate to ubuntu:

Copy your certificate in **PEM** format (the format that has ----BEGIN CERTIFICATE---- in it) into 

    /usr/local/share/ca-certificates 
and name it with a .crt file extension. Then, run this command:


    $: sudo update-ca-certificates

## Authentification

### MITM Service

As you have noticed in the example above, the user name sent to the proxy has this format:

    username-configID

Which gives for the config 1:

    proxy_username-1

### REST API

The REST API uses basic auth for authentication. Here is an example of curl using the default credentials in the **docker-compose** file:

```bash
$: curl -X GET \
    http://localhost:443/auth/get_token \
    -H 'Authorization: Basic YXBpX3VzZXJuYW1lOjJDOGZkcFp3R0FZdEt3c2ZEVkZMb3F0R3N0MlVGYnhDMkVyCg=='
```

**YXBpX3VzZXJuYW1lOjJDOGZkcFp3R0FZdEt3c2ZEVkZMb3F0R3N0MlVGYnhDMkVyCg==** is the base64 of **api_username:2C8fdpZwGAYtKwsfDVFLoqtGst2UFbxC2Er**

# Configurations

## JSON Format

A configuration is a JSON that contains all the data needed by the MITM proxy to clean the requests.

The key in S3 for each config is: s3://hermes_s3_bucket/configs/config_id=1/conf.json

Here is a speudo example of a config:

```json
{
    "config_name": "Config name given by the user",
     
    // ---------------
    // ---- Connection : close
    "do_not_modify_connection_header": false,                           // default: false
     
     
    // ---------------
    // ---- SSL / TLS
     
    "ssl" : {
        "verify_ssl" : false,                                           // default: false
        "version" : "PROTOCOL_TLS",                                     // default: "PROTOCOL_TLS"
        "ciphers": "AES256-GCM-SHA384:AES128-SHA:AES256-SHA:DES-CBC3-SHA",     // default: NOT SET / null
        "signatures": "ECDSA+SHA256:RSA+SHA256"                         // default: NOT SET / null
    },
     
     
    // ---------------
    // ---- HTTP 2
     
    "http2": "NO",                                                      // default: "NO"
     
     
    // ---------------
    // ---- Blacklist
     
    "blacklist": [                                                      // default: Empty list
                    ".*google.*",
                    ".*youtube.*",
                 ],
     
    // ---------------
    // ---- Headers freeze
     
    "headers_freeze":   [                                               // default: empty list
                            {
                                "host_regex": ".*amazon.*",
                                "headers" : ["cookie", "user-agent"],
                                "max_requests": 1000 //can be -1 for infinity
                            }
                        ],
     
     
    // ---------------
    // ---- Headers
     
    //default: NOT SET / null
    "headers": "(function(data_attribute_stringified) {var headers_obj = eval(data_attribute_stringified); return JSON.stringify([headers_obj[0]]);})('DATA_ATTRIBUTE_INPUT')",
     
     
    // ---------------
    // ---- Proxy (plain mode)
     
    "proxy" : {                                                         // default: NOT SET / null
        "host": "website.com",
        "port": 222,
        "username": null,
        "password": null
    }
     
    // ---------------
    // ---- Site blacklist response
     
    "site_blacklist_response" : ''                                      // default: NOT SET / empty String / null
 
     
}
```

## UI Format

You can use the UI to modify the config :

 - http://localhost/editconfig?config_id_url=1: The web server for the UI

Here is the interface:

![ConfigUI](images/config_ui.png)

Do not forget to save the config, after each modification:

![SaveConfigUI](images/save_config.png)

# UI Testing

You can test a config with a curl, do not forget to save the config before:

![ConfigTest](images/config_test.png)

Once the test finishes, the UI will display a detailed log of each operation done.

This log is very helpful to debug / finetune your config and check that the requested behaviour is respected.

# Features

We will use the **UI** to modify the config.

## SSL handshake

Here you can modify the SSL handshake made with the target server.

 - ssl→verify_ssl: make sure the server certificate is valid: false or true 
 - ssl→version:
    - PROTOCOL_TLS: will select the highest protocol possible
    - PROTOCOL_TLSv1
    - PROTOCOL_TLSv1_1
    - PROTOCOL_TLSv1_2
    - Source: https://docs.python.org/3/library/ssl.html
 - ssl→ciphers:
    - Source: https://www.openssl.org/docs/man1.0.2/man1/ciphers.html
 - ssl→signatures:
    - Source: https://www.openssl.org/docs/man1.1.0/man3/SSL_CTX_set1_sigalgs_list.html
    - Check your signature: https://clienttest.ssllabs.com:8443/ssltest/viewMyClient.html

![SSL Config](images/ssl_config.png)


## HTTP2

You can make the end request with the target server use the HTTP/2 protocol.

Just put **"YES"** for the field **http2**, put **"NO"** otherwise.

![HTTP2](images/http2.png)


## Proxy

Hermes provides two modes for Proxy selection:

 - Simple mode: for **static** proxy config
 - Advanced mode: for **programmatic** proxy selectionc

### Simple Proxy

The simple proxy can be used by checking the box **use Simple mode** and by providing a json node with this format:

```json
{
    "host": "someproxy.provider.com",
    "password": "proxy-password-hasd-to-guess",
    "port": 8080,
    "username": "my_username",
    "type":"http"
}
```

for a no Authentification based proxy, you can use this config:

```json
{
    "host": "someproxy.provider.com",
    "port": 8080,
    "username": null,
    "password": null,
    "type":"socks4"
}
```

![SimpleProxy](images/simple_proxy.png)

### Advanced Proxy

The advanced proxy can be used by **unchecking** the box **use Simple mode

NodeJS version 14.x will be running this code / JS function.

You should, at the end, console.log a stringified dictionnary like this:

```js
console.log(
    JSON.stringify(
            {
                "host": "someproxy.provider.com",
                "password": "proxy-password-hasd-to-guess",
                "port": 8080,
                "username": "my_username",
                "type":"socks5",
                "data": "some index to track the selected proxy"
            }
        )
    );
```

The **data field** is used to pass data to Hermes. It can be, the selected proxy id, etc ...

![AdvancedProxy](images/advanced_proxy.png)

## Headers

With Hermes, you have the ability to modify the HTTP headers on-the-fly programmatically.

The JS interpreter running this code **does not support Promises nor Async functions**. It is just a simple JS evaluation light engine.

The **headers_obj** var contains the list of the orginal headers send by the client.

You should, at the end, console.log a stringified list of arrays (each one with 2 elements: key and value):

```
JS functions for Headers should return a Stringified object with this format:

[['header_key_1', 'header_val_1'],['header_key_2', 'header_val_2'],['header_key_3', 'header_val_3'], ....]
```

![Headers](images/headers.png)

## Headers Freeze

This feature will allow you to freeze headers for recurrent requests on a given domain name

Here is an example of config:

![Headers Freeze](images/headers_freeze.png)

### Input format:

- host_regex: this node will be activated when this regex hits the requested ressource URL
- headers: list of headers that will be persisted
- max_requests: number of times, the headers will be persisted. -1 for infinity. After this limit, the stored data is purged and new values will be stored.


### How does it work:

The **host_regex** works as a filter / regex for the node to activate.

When a host is hit, the MITM service will check if there is data stored for this **host_regex** and **headers**.

If there is data stored and **max_requests** is not exceeded, the MITM will modify the **headers** in the request with the stored values.

If there is no data and the requests contains all the **headers**, the MITM will store these values.

### Use cases:
- Cookie persistence / re-use
- Fingerprint consistence


## Sites

A site is a configuration that allows you to **engage an action** when a **condition is met** on a specific websites.

We will see two sections:
 - Site config: How to configure a site to detect a specific condition
 - Site reply: How to configure a JS code to be ran when this condition is met

### Sites Config

A site is identified by a **regex** that hits all the URL the MITM proxy will request.

On the main page of the **UI**, you can add a new site / regex:

![Add site](images/sites.png)

The JS code will be executed by Node and should return 1 or 0.

![Site details](images/site_details.png)

Your JS code will have access to :

 - reply: HTTP response
    - code: response code
    - header: response headers
    - data: response data
 - proxy: the proxy used in the config
    - host: proxy host
    - auth: auth is used
    - log: response code
        - stdout: the console log of the JScode to select the proxy
        - stderr: error messages
        - data_carried: data returned by your JS code to select the proxy
        - note: system info

An example of JS code would be: 
```js
if (String(input_data['reply']['data']).includes("blacklisted")){
  console.log(1);
}else{
  console.log(0);
}
```


### Sites Reply

The reply is configured on the **Config UI** page and the JS code is executed only if the Site detection code will return **1**.

![Site Reply](images/site_reply.png)

The JS code has access to the same data as in Site Config (above).

You can see here that the **data field** in your **Advanced proxy config** can be useful to take a Proxy targeted response.