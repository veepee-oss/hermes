# --------------------------------------
# ---------- Backend Base Image --------
# --------------------------------------
FROM ubuntu:18.04 AS hermes-backend-base

# ---- Install python3.8 and pip3
RUN apt-get update
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update

RUN apt-get install -y python3.8 python3.8-distutils python3.8-dev wget 
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.8 get-pip.py

# ---- Install Hermes backend dependencies
RUN apt-get install -y gcc musl-dev libffi-dev openssl libssl-dev cargo g++ make curl
ADD . /app/hermes
WORKDIR /app/hermes/backend
RUN pip3 install -r ./requirements.txt

# ---- Install FlexSSL extension
WORKDIR /app/hermes/packages/flexssl
RUN python3.8 setup.py install

# --------------------------------------
# ---------- MITM Service Image --------
# --------------------------------------
FROM hermes-backend-base AS hermes-backend-mitm

# ---- Install MITM  backend dependencies
RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get update
RUN apt install -y uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev 
RUN apt install -y nodejs
RUN node -v

# ---- Install UWSGI with python3.8 bindings
RUN cd /tmp
RUN export PYTHON=python3.8 && uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python38"
RUN mv python38_plugin.so /usr/lib/uwsgi/plugins/python38_plugin.so
RUN chmod 644 /usr/lib/uwsgi/plugins/python38_plugin.so 

# ---- Service
EXPOSE 8080
WORKDIR /app/hermes/backend
CMD ["./start_mitm.sh"]


# --------------------------------------
# ---------- REST API Image ------------
# --------------------------------------
FROM hermes-backend-base AS hermes-backend-api

# ---- Service
EXPOSE 443
WORKDIR /app/hermes/backend
CMD ["python3.8","-u","api.py","-p", "443"]


# --------------------------------------
# ---------- Webdev frontend Image -----
# --------------------------------------
FROM ubuntu:18.04 AS hermes-frontend-webdev


# ---- Install NodeJS and NPM
RUN apt-get update
RUN apt-get -y install curl
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get update
RUN apt install -y nodejs build-essential

# ---- Install VueJS and Yarn
RUN node -v
RUN npm install -g @vue/cli
RUN npm install -g @vue/cli-init
RUN npm install -g yarn

# ---- Link the webdev frontend server to localhost API (relative path as same VM)
RUN echo :443 >> /tmp/hermes_stored_endpoint.bin

# ---- Service
EXPOSE 80
ADD . /app/hermes
WORKDIR /app/hermes/frontend
RUN yarn install
CMD ["yarn","serve"]