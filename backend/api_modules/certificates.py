import json
from operator import itemgetter

import utils.s3_utils

import api_modules.utils

HERMES_CA_PROVIDED_CERT = "ca-hermes.crt"
HERMES_CA_CERT_KEY = "ca-hermes.key"

def get_public_certificate():
    public_cert = utils.s3_utils.get_content(HERMES_CA_PROVIDED_CERT)
    if public_cert is None:
        return 'Not found !', 404
    else:
        response = {"public_cert":public_cert}
        return api_modules.utils.flask_response_json(True, response)

def get_private_certificate():
    private_cert = utils.s3_utils.get_content(HERMES_CA_CERT_KEY)
    if private_cert is None:
        return 'Not found !', 404
    else:
        response = {"private_cert":private_cert}
        return api_modules.utils.flask_response_json(True, response)
