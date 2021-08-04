# FlexSSL Python Package

Python3 package to expose OpenSSL C functions to Python.

You will need these dependencies:
```bash
$: apt-get update
$: apt-get install libffi-dev libssl-dev
$: apt-get install python3.8-dev #Depends on your python version
```

# Examples:

## set_sigalgs

Change Signature Algorithms for a given SSL Context:

```python
import ssl
import flexssl

used_version = ssl.PROTOCOL_TLS
res_context = ssl.SSLContext(used_version) 

flexssl.set_sigalgs("ECDSA+SHA256:ECDSA+SHA384:ECDSA+SHA512:RSA-PSS+SHA256:RSA-PSS+SHA384:RSA-PSS+SHA512:RSA+SHA256:RSA+SHA384:RSA+SHA512:ECDSA+SHA1:RSA+SHA1", res_context)
```