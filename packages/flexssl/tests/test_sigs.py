import ssl
import flexssl

used_version = ssl.PROTOCOL_TLS
res_context = ssl.SSLContext(used_version) 

flexssl.set_sigalgs("ECDSA+SHA256:ECDSA+SHA384:ECDSA+SHA512:RSA-PSS+SHA256:RSA-PSS+SHA384:RSA-PSS+SHA512:RSA+SHA256:RSA+SHA384:RSA+SHA512:ECDSA+SHA1:RSA+SHA1", res_context)