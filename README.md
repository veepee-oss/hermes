# Hermes MITM Proxy

Hermes is a **man-in-the-middle proxy** that allows HTTP, HTTPS and HTTP/2 trafic interception, inspection and modification. 

It can be used for application testing and debugging, privacy measurements, penetration testing and network monitoring.

It is composed of 3 main building blocks:

 - A. the MITM service
 - B. REST API
 - C. Frontend GUI

Backend components are written in Python and the Frontend leverages the VueJS framework.

# News

See [CHANGELOG.md](CHANGELOG.md) for detailed information about latest features.

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed information about how to contribute to the project.

# Installation (Easy - Dev)

We have packed a [docker-compose](https://docs.docker.com/compose/install/) file that allows you to setup all the stack in one command line:

    $: docker-compose up

This will summon all the components needed to run the service on the same environment. If you summon this on localhost:

 - http://localhost: The web server for the UI
 - http://localhost:443/ : The REST API service
 - http://localhost:8080/ : The MITM service

You should modify the environment variables in the docker-compose file ! 

A vanilla / hello world config is created with id = 1.

Please be aware that this deployment is not for production !

# Installation (Advanced - Production)

In this section, we will detail the installation steps for the 3 main building blocks of Hermes.

## Prerequisites

Make sure you have python3.8 installed with pip3 as a package manager.

You will also need a Redis server / cluster and an S3 compatible endpoint.

 - Redis: check the [docker install](https://hub.docker.com/_/redis) for example
 - S3: you can use [Minio with docker](https://hub.docker.com/r/minio/minio/) or AWS S3

Each component will use a list of **Environment variables** that you will need to configure before running the program.

We will be using **Ubuntu 18.04** for the installation procedure.

You should maybe add this repo for full python3.8 support:

    $: apt-get update
    $: apt install -y software-properties-common
    $: add-apt-repository -y ppa:deadsnakes/ppa
    $: apt-get update
    $: apt-get install python3.8

## A. the MITM service

### Location in the Repo:
    ./backend/mitm.py
    
### Install dependencies

Install **Ubuntu packages**:

    $: apt-get update
    $: apt-get install -y gcc musl-dev libffi-dev openssl libssl-dev cargo g++ make curl wget
    $: apt-get install -y python3.8-distutils python3.8-dev

Install **Python3.8 packages** with pip3:

    $: pip3 install -r ./backend/requirements.txt

Install FlexSSL extension:

    $: cd packages/flexssl
    $: python3.8 setup.py install

Install **UWSGI** with **Python3.8 support**:

    $: apt-get update
    $: apt-get install -y uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev
    
    $: cd ~
    $: export PYTHON=python3.8
    $: uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python38"
    $: sudo mv python38_plugin.so /usr/lib/uwsgi/plugins/python38_plugin.so
    $: sudo chmod 644 /usr/lib/uwsgi/plugins/python38_plugin.so

Install **NodeJS 14.x**:

    $: apt-get update
    $: curl -sL https://deb.nodesource.com/setup_14.x | bash -
    $: apt-get update
    $: apt-get install -y nodejs
    $: node -v

### Environment variables

You will need to fill these Environment variables:

    # Redis Server / Cluster
    export REDIS_URL="redis-host.my-infra.com"			    # Redis host
    export REDIS_PORT="6379"			                    # Redis port
    
    # S3 compatible endpoint
    export S3_API_KEY_ID="this_is_a_key_id"				    # S3 credentials
    export S3_API_ACCESS_KEY="this_is_an_access_id"		        # S3 credentials
    export S3_URL_ENDPOINT="http://some-domain.com:9000"       # S3 endpoint, will use AWS if not specified
    export S3_BUCKET="this_is_an_s3_bucket"				    # S3 bucket
	
	# Credentials to secure the MITM proxy
	export PROXY_USERNAME="hermes_mitm_username"		        # Username
	export PROXY_PASSWORD="hermes_mitm_password"		        # Password

### Custom config

You can customize the MITM proxy configuration file:

    ./backend/deploy.ini

### Launch commands

To run the MITM, go to the repo folder and run:

    $: cd ./backend
    $: uwsgi --ini deploy.ini

To Kill the MITM proxy:

    $: kill -9 `cat /tmp/mitm_proxy.pid`

Or use Kill-port to kill apps listening on port 8080:

    $: npx kill-port 8080


## B. REST API

### Location in the Repo:
    ./backend/api.py
    
### Install dependencies

Install **Ubuntu packages**:

    $: apt-get update
    $: apt-get install -y gcc musl-dev libffi-dev openssl libssl-dev cargo g++ make curl wget
    $: apt-get install -y python3.8-distutils python3.8-dev

Install **Python3.8 packages** with pip3:

    $: pip3 install -r ./backend/requirements.txt

Install FlexSSL extension:

    $: cd packages/flexssl
    $: python3.8 setup.py install

### Environment variables

You will need to fill these Environment variables:

    # Redis Server / Cluster
    export REDIS_URL="redis-host.my-infra.com"			    # Redis host
    export REDIS_PORT="6379"			                    # Redis port
    
    # S3 compatible endpoint
    export S3_API_KEY_ID="this_is_a_key_id"				    # S3 credentials
    export S3_API_ACCESS_KEY="this_is_an_access_id"		        # S3 credentials
    export S3_URL_ENDPOINT="http://some-domain.com:9000"       # S3 endpoint, will use AWS if not specified
    export S3_BUCKET="this_is_an_s3_bucket"				    # S3 bucket
    
    # API secret keys
    export SECRET_KEY_APP="random_long_string_api"		        # Secret key API
	
	# Credentials to secure the REST API
	export API_USERNAME="hermes_api_username"			    # Username
	export API_PASSWORD="hermes_api_password"			    # Password
	
	# API can curl the MITM, please specify the mitm endpoint
	export MITM_TEST_URL="127.0.0.1"			            # MITM testing Endpoint
	export MITM_TEST_PORT="8080"			                    # MITM testing port

	# Credentials to call the MITM proxy
	export PROXY_USERNAME="hermes_mitm_username"		        # Username
	export PROXY_PASSWORD="hermes_mitm_password"		        # Password

### Custom config

You can customize the API configuration file:

    ./backend/config.json

### Launch command

For a vanilla HTTP server (not secured)

    $: cd ./backend
    $: python3.8 -u api.py

For a secured HTTPS server

    $: cd ./backend
    $: python3.8 -u api.py -p 443 -c '/certs/fullchain.pem' -k '/certs/privkey.pem'



## C. Frontend GUI

### Location in the Repo:
    ./frontend
    
### Install dependencies

You will need to have **NodeJS 14.x** and **NPM package manager** installed.

Install **Ubuntu packages**:

    $: apt-get update
    $: apt-get install -y build-essential

Install **NodeJS packages**:

    $: npm install -g @vue/cli
    $: npm install -g @vue/cli-init
    $: npm install -g yarn
    


### Launch commands

You will be asked to give the API endpoint when deploying or serving.

Serve in **development** mode

    $: yarn serve

**Build** for production

    $: yarn build

Deploy to **AWS S3** (example)

    $: yarn build
    $: python3.8 -m awscli s3 cp dist s3://mys3bucket/ --recursive


# Usage 
See the **[Wiki](docs/index.md)** for detailed information and tutorials about how to use Hermes.

You can also check the **[API](docs/api.md)** doc.

# LICENSE
This project is licensed under the **ISC [LICENSE](LICENSE)**.