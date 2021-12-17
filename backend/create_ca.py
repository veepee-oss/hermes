import datetime

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import utils.s3_utils

HERMES_CA_PROVIDED_PATH =  "/etc/ssl/private/"
HERMES_CA_PROVIDED_CERT_FILE = "ca-hermes.crt"
HERMES_CA_CERT_KEY_FILE = "ca-hermes.key"

#################CERTIFICATE AUTHORITY #####################

root_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Paris"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Paris"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"hermes"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"hermes-ca"),
])
root_cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    root_key.public_key()
).add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True,
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=3650)
).sign(root_key, hashes.SHA256(), default_backend())


root_key_str = root_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

root_cert_str = root_cert.public_bytes(
        encoding=serialization.Encoding.PEM,
    )

with open(HERMES_CA_PROVIDED_PATH+HERMES_CA_CERT_KEY_FILE, "wb") as f:
    f.write(root_key_str)

with open(HERMES_CA_PROVIDED_PATH+HERMES_CA_PROVIDED_CERT_FILE, "wb") as f:
    f.write(root_cert_str)


#Push to S3 the certificates
utils.s3_utils.push_string_s3_file(root_cert_str,HERMES_CA_PROVIDED_CERT_FILE)
utils.s3_utils.push_string_s3_file(root_key_str,HERMES_CA_CERT_KEY_FILE)