import utils.config_handler
import utils.s3_utils
import proxy_modules.backbone
import proxy_modules.utils

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

HERMES_CA_PROVIDED_PATH =  "/etc/ssl/private/"
HERMES_CA_PROVIDED_CERT_FILE = "ca-hermes.crt"
HERMES_CA_CERT_KEY_FILE = "ca-hermes.key"

SERVER_CONFIG = utils.config_handler.load_json_config()

#Retrieve the Certificate Authority certs
ca_public_key_text = utils.s3_utils.get_content(HERMES_CA_PROVIDED_CERT_FILE)
ca_private_key_text = utils.s3_utils.get_content(HERMES_CA_CERT_KEY_FILE)

ca_public_key = x509.load_pem_x509_certificate(bytes(ca_public_key_text, 'utf-8'), default_backend())
ca_private_key = load_pem_private_key(bytes(ca_private_key_text, 'utf-8'), None, default_backend())

# Run the MITM
proxy_modules.backbone.ManInTheMiddle(ca_public_key, ca_private_key).run()