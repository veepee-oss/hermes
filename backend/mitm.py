import ssl
import os

import utils.config_handler
import proxy_modules.backbone
import proxy_modules.utils

SERVER_CONFIG = utils.config_handler.load_json_config()
USER_PROVIDED_CERT = "/etc/ssl/private/mitm.crt"
USER_PROVIDED_CERT_KEY = "/etc/ssl/private/mitm.key"

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

if (os.path.isfile(USER_PROVIDED_CERT) and os.path.isfile(USER_PROVIDED_CERT_KEY)):
    # Use user provided certificate
    ssl_context.load_cert_chain(USER_PROVIDED_CERT, USER_PROVIDED_CERT_KEY)
else:
    # Generate random certificate
    rsa_key = proxy_modules.utils.RSA()
    ssl_context.load_cert_chain(rsa_key.certificate_file, rsa_key.private_key_file)

# Run the MITM
proxy_modules.backbone.ManInTheMiddle(ssl_context).run()