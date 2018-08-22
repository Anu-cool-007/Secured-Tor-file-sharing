from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random


def aes_encrypt(data: bytes):
    random_gen = Random.new()
    key = random_gen.read(AES.block_size)
    iv = random_gen.read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    msg = iv + cipher.encrypt(data)
    return key, msg


def rsa_encrypt(data: bytes, public_key: bytes):
    key = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(data)
    return ciphertext


def encrypt(public_key: bytes, file_path: str):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return "File does not exist"

    key, enc_data = aes_encrypt(data)
    enc_key = rsa_encrypt(key, public_key)

    with open(file_path + ".enc", "wb") as f:
        f.write(enc_key)
        f.write(enc_data)

    return "Encrypted Successfully"
