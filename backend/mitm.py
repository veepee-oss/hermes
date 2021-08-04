import ssl

import utils.config_handler
import proxy_modules.backbone
import proxy_modules.utils

SERVER_CONFIG = utils.config_handler.load_json_config()

# Generate the Certificate and the SSL context
rsa_key = proxy_modules.utils.RSA()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.load_cert_chain(rsa_key.certificate_file, rsa_key.private_key_file)

# Run the MITM
proxy_modules.backbone.ManInTheMiddle(ssl_context).run()