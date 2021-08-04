# REST API routes

We will detail here the API Routes exposed by the REST API.

# Table of contents

1. [Authentification](#authentification)
    1. [Basic Auth](#basic-auth)
    2. [Token](#fetch-token)
2. [Configurations](#configurations)
    1. [New Config](#new-config)
    2. [Update Config](#update-config)
    3. [List Configs](#list-configs)
    4. [Delete Config](#delete-config)
    5. [Get Config](#get-config)
    6. [Get Config Meta Data](#get-config-meta-data)
    7. [Purge Config Meta Data](#purge-config-meta-data)
3. [Logging](#logging)
    1. [Fetch all logs](#fetch-all-logs)
    2. [Fetch Xray log](#fetch-xray-log)
    3. [Fetch BL logs](#fetch-bl-logs)
    4. [Flush Redis](#flush-redis)
    5. [Flush all Redis](#flush-all-redis)
4. [Summary](#summary)
5. [Testing](#testing)
6. [Sites](#sites)
    1. [New Site](#new-site)
    2. [Update Site](#update-site)
    3. [List Sites](#list-sites)
    4. [Delete Site](#delete-site)
    5. [Get Site](#get-site)

# Authentification

The API uses **basic auth** for authentication. Here is an example of curl using the default credentials in the **docker-compose** file:

## Basic Auth

```bash
$: curl -X GET \
    http://localhost:443/auth/get_token \
    -H 'Authorization: Basic YXBpX3VzZXJuYW1lOjJDOGZkcFp3R0FZdEt3c2ZEVkZMb3F0R3N0MlVGYnhDMkVyCg=='
```

**YXBpX3VzZXJuYW1lOjJDOGZkcFp3R0FZdEt3c2ZEVkZMb3F0R3N0MlVGYnhDMkVyCg==** is the base64 of **api_username:2C8fdpZwGAYtKwsfDVFLoqtGst2UFbxC2Er**

That can be computed by:
```bash
$: echo 'api_username:2C8fdpZwGAYtKwsfDVFLoqtGst2UFbxC2Er' | base64
```

In the following doc, we will refer to this string as: **BASE64_CREDS** and a Curl would be presented like this:

```bash
$: curl -X GET \
    http://localhost:443/auth/get_token \
    -H 'Authorization: Basic BASE64_CREDS'
```

## Fetch Token

Will get a token from the API. This Token can be used afterwards as a username without a password.

Request

```bash
$: curl -X GET \
    http://localhost:443/auth/get_token \
    -H 'Authorization: Basic BASE64_CREDS'
```

Response

```js
{
    "token": "some string containing the token"
}
```

To get the new **BASE64_CREDS** you can run:

```bash
$: echo 'received_token_long_string:' | base64
```

# Configurations

These route will allow you to manipule Configurations programmatically.

## New Config

Will create a new config based on a JSON config.

Request

```bash
$: curl -X POST \
  http://localhost:443/configs/new \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{
    "config":   {
        "config_name": "Config name given by the user",
         
         
        "ssl" : {
            "verify_ssl" : false,                                          
            "version" : "PROTOCOL_TLS",                                    
            "ciphers": "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"     
        },
         
        "http2": "NO", 
         
        "headers": null,
         
        "data_transformations" : [],
         
        "proxy" : null,
         
        "waterfall_requests" : []
         
    }
}'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "config_id": 2
    }
}
```


## Update Config

Will update an existing config based on a JSON config.

Here, we will update the **config_id : 1**.

Request

```bash
$: curl -X POST \
  http://localhost:443/configs/update/1 \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{
    "config":   {
        "config_name": "Config name given by the user new",
         
         
        "ssl" : {
            "verify_ssl" : false,                                          
            "version" : "PROTOCOL_TLS",                                    
            "ciphers": "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"     
        },
         
        "http2": "NO", 
         
        "headers": null,
         
        "data_transformations" : [],
         
        "proxy" : null,
         
        "waterfall_requests" : []
         
    }
}'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "config_id": 1
    }
}
```


## List Configs

List current configs.

Request

```bash
$: curl -X GET \
  http://localhost:443/configs/list \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": [
        {
            "id": 2,
            "key": "configs/config_id=2/conf.json"
        },
        {
            "id": 1,
            "key": "configs/config_id=1/conf.json"
        }
    ]
}
```


## Delete Config

Will delete a config

Request

```bash
$: curl -X GET \
  http://localhost:443/configs/delete/5 \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": "Deleted !"
}
```

## Get Config

Will fetch a config

Request

```bash
$: curl -X GET \
  http://localhost:443/configs/get/3 \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "config_name": "test 3",
        "data_transformations": [],
        "do_not_modify_connection_header": false,
        "headers": null,
        "http2": "NO",
        "proxy": null,
        "ssl": {
            "ciphers": null,
            "verify_ssl": false,
            "version": "PROTOCOL_TLS"
        },
        "waterfall_requests": []
    }
}
```

## Get Config Meta Data

Will get config meta data like the Headers freezed.

See the **[Wiki](index.md)** for this feature.

Request

```bash
$: curl -X GET \
  http://localhost:443/configs/get_meta_data/6 \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "headers_freeze_data": [
            {
                "b64_key": "LippcGlmeS4qLWFjY2VwdC1lbmNvZGluZy11c2VyLWFnZW50",
                "counter": 1,
                "data": [
                    [
                        "user-agent",
                        "python-requests/2.25.1"
                    ],
                    [
                        "Accept-Encoding",
                        "gzip, deflate"
                    ]
                ],
                "plain_key": ".*ipify.*-accept-encoding-user-agent"
            },
            {
                "b64_key": "LippcGlmeS4qLWFjY2VwdC1lbmNvZGluZy10ZXN0LWhlYWRlci11c2VyLWFnZW50",
                "counter": 2,
                "data": [
                    [
                        "user-agent",
                        "python-requests/2.25.1"
                    ],
                    [
                        "Accept-Encoding",
                        "gzip, deflate"
                    ],
                    [
                        "test-header",
                        "yo"
                    ]
                ],
                "plain_key": ".*ipify.*-accept-encoding-test-header-user-agent"
            }
        ]
    }
}
```

## Purge Config Meta Data

You can purge the meta data for a given config:

Request

```bash
$: curl -X POST \
  http://localhost:443/configs/headers_freeze/purge \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{  
    "config_id": "6",
    "b64key": "LippcGlmeS4qLWFjY2VwdC1lbmNvZGluZy11c2VyLWFnZW50"
}'
```

Response

```js
Done ! 200
```

# Logging

These routes will allow you to handle the Logs.

## Fetch all logs

Fetch the usage logs for all the configs.

Request

```bash
$: curl -X GET \
  http://localhost:443/logs/fetch_all_logs \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

## Fetch Xray log

You can add the Header **xRayTrackingID** in your HTTP request to have an advanced logging.

This should result for a curl like this :

```bash
$: curl -X GET \
    https://api.ipify.org?format=json \
    --proxy http://proxy_username-1:PVnkJazW2weJ6EcyZKgoZ7cNbckXVeGje4P@localhost:8080 \
    --insecure \
    -H 'Content-Type: application/json'\
  -H 'xRayTrackingID: 1232'
```

Note: This is an example of curl using the default credentials in the **docker-compose** file.

To fetch the detailed log for this **Xray**:

Request

```bash
$: curl -X POST \
  http://localhost:443/logs/fetch_xray_log \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{
    "xrayID": "1232"
}'
```

Response (BSON format)

```js
[
    {
        "message": "2021-06-04 15:17:05 [XRAY: 1232] [INFO] Step 1.1. Initiating xRay tracing for this request !",
        "date": "2021-06-04 15:17:05",
        "data": {},
        "tag": "INFO"
    },
    ...
    {
        "message": "2021-06-04 15:17:08 [XRAY: 1232] [SUCCESS] Step 3. Request done !",
        "date": "2021-06-04 15:17:08",
        "data": {},
        "tag": "SUCCESS"
    }
]
```

## Fetch BL logs

Fetch the Sites blacklist detections stats:

Request

```bash
$: curl -X GET \
  http://localhost:443/logs/fetch_bl_logs \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```


## Flush Redis

Fetch all the stats stored in Redis

Request

```bash
$: curl -X GET \
  http://localhost:443/logs/flush_redis \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "msg": "Stats flushed !"
    }
}
```

## Flush all Redis

Fetch all Redis (stats + configs stored in RAM)

Request

```bash
$: curl -X GET \
  http://localhost:443/logs/flush_all_redis \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "msg": "Redis flushed !"
    }
}
```


# Summary

Route to fetch all stats in one api call ! Use GZIP compression for this !

Request

```bash
$: curl -X GET \
  http://localhost:443/summary \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -H 'Accept-Encoding: application/gzip'
```


# Testing

You are able to test the MITM proxy without performing a Curl but you can use the REST API for this.

The API will communicate with MITM proxy and will perform the tes for you.

Request

```bash
$: curl -X POST \
  http://localhost:443/test_curl \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \   
-d '{
    "url": "https://api.ipify.org?format=json",
    "method": "GET",
    "headers": [["Content-Type","application/json"]],
    "data": "",
    "config_id": "1"
}'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "response": "{\"ip\":\"some.ip.hidden.here\"}",
        "xray_token": "9435559040239_1623410277"
    }
}
```

# Sites

See the **[Wiki](index.md)** for this feature.

## New Site

Create a new site:

Request

```bash
$: curl -X POST \
  http://localhost:443/sites/new \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{
    "site": {
        "regex": "some_regex_ere",
        "blacklist_detection": ""
    }
}'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "site_hex": "hexed_regex_as_output"
    }
}
```

## Update Site

Update a given site:

Request

```bash
$: curl -X POST \
  http://localhost:443/sites/update \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{
    "site": {
        "regex": "new_regex_here",
        "blacklist_detection": "new function"
    }
}'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "site_hex": "new_hexed_regex_as_output"
    }
}
```

## List Sites

List the available sites

Request

```bash
$: curl -X GET \
  http://localhost:443/sites/list \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' 
```


## Delete Site

Delete a given site:

Request

```bash
$: curl -X POST \
  http://localhost:443/sites/delete \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json' \
  -d '{
    "site_hex": "some_hexed_regex"
}'
```

Response

```js
Deleted, 200
```

## Get Site

Fetch a site configuration.

Request

```bash
$: curl -X GET \
  http://localhost:443/sites/get/some_hexed_regex \
  -H 'Authorization: Basic BASE64_CREDS' \
  -H 'Content-Type: application/json'
```

Response

```js
{
    "response_code": true,
    "response_msg": {
        "blacklist_detection": "",
        "regex": "some_hexed_regex"
    }
}
```