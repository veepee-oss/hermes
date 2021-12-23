#!/bin/bash

python3.8 create_ca.py
uwsgi --ini deploy.ini