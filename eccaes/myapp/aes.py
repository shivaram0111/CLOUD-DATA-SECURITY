from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def pad(data):
    while len(data) % 16 != 0:
        data += b' '
    return data

def encrypt(plain_text, key):
    cipher = AES.new(pad(key), AES.MODE_CBC)
    cipher_text = cipher.encrypt(pad(plain_text))
    return base64.b64encode(cipher.iv + cipher_text)

def decrypt(encrypted_text, key):
    encrypted_text = base64.b64decode(encrypted_text)
    iv = encrypted_text[:16]
    cipher_text = encrypted_text[16:]
    cipher = AES.new(pad(key), AES.MODE_CBC, iv)
    decrypted_text = cipher.decrypt(cipher_text)
    return decrypted_text.rstrip(b' ')