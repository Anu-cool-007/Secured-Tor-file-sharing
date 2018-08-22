import os

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


def rsa_decrypt(data: bytes, private_key: RSA._RSAobj):
    cipher = PKCS1_OAEP.new(private_key)
    message = cipher.decrypt(data)
    return message


def aes_decrypt(key: bytes, data: bytes):
    iv = data[:AES.block_size]
    message = data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(message)


def decrypt(private_key: bytes, file_path: str):
    private_key = RSA.importKey(private_key)
    key_size = (private_key.size() + 1) // 8

    try:
        with open(file_path, "rb") as f:
            enc_key = f.read(key_size)
            enc_data = f.read()
    except FileNotFoundError:
        return "File does not exist"
    try:
        key = rsa_decrypt(enc_key, private_key)
    except ValueError:
        return "Could not decrypt the key"

    data = aes_decrypt(key, enc_data)

    with open(os.path.splitext(file_path)[0], "wb") as f:
        f.write(data)

    return "Decrypted successfully"
