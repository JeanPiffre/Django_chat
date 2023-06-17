import rsa
import os

def generate_keys(filename):
    publicKey, privateKey = rsa.newkeys(512)

    public_key_file = os.path.join("publicKey", f"{filename}.pem")
    private_key_file = os.path.join("privateKey", f"{filename}.pem")

    with open(public_key_file, "wb") as file:
        file.write(publicKey.save_pkcs1())

    with open(private_key_file, "wb") as file:
        file.write(privateKey.save_pkcs1())

def encrypt(message, public_key_filename):
    public_key_file = os.path.join("publicKey", f"{public_key_filename}.pem")

    with open(public_key_file, "rb") as file:
        publicKey = rsa.PublicKey.load_pkcs1(file.read())

    encMessage = rsa.encrypt(message.encode(), publicKey)

    return encMessage

def decrypt(encMessage, private_key_filename):
    private_key_file = os.path.join("privateKey", f"{private_key_filename}.pem")

    with open(private_key_file, "rb") as file:
        privateKey = rsa.PrivateKey.load_pkcs1(file.read())

    decMessage = rsa.decrypt(encMessage, privateKey).decode()

    return decMessage