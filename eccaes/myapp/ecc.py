from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet
import os
import base64

server_private_key = ec.generate_private_key(ec.SECP384R1())
server_public_key = server_private_key.public_key()
server_public_key_bytes = server_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
server_public_key = serialization.load_pem_public_key(server_public_key_bytes)

client_private_key = ec.generate_private_key(ec.SECP384R1())
client_public_key = client_private_key.public_key()
client_public_key_bytes = client_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
client_public_key = serialization.load_pem_public_key(client_public_key_bytes)

server_shared_key = server_private_key.exchange(ec.ECDH(), client_public_key)
client_shared_key = client_private_key.exchange(ec.ECDH(), server_public_key)

derived_key_server = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'handshake data'
).derive(server_shared_key)

derived_key_client = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'handshake data'
).derive(client_shared_key)

assert derived_key_server == derived_key_client

fernet_key = Fernet(base64.urlsafe_b64encode(derived_key_server))