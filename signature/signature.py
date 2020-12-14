from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64
import cryptography.exceptions


def generate_keypair(password=None):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )
    if password is None:
        encryption = serialization.NoEncryption()
    else:
        encryption = serialization.BestAvailableEncryption(password)
    key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=encryption,
    )
    pub = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return (key, pub)

def sign(payload, key, password=None):
    private_key = serialization.load_pem_private_key(
        data=key,
        password=password,
        backend=default_backend(),
    )
    signature = private_key.sign(
        payload,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature

def verify(payload, signature, pub):
    public_key = load_pem_public_key(pub, default_backend())
    # Perform the verification.
    try:
        public_key.verify(
            signature,
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except cryptography.exceptions.InvalidSignature as e:
        print('ERROR: Payload and/or signature files failed verification!')
        return False
    return True


def _generate_keypair():
    (key, pub) = generate_keypair("ABC")
    with open('private.key', 'wb') as f:
        f.write(key)
    with open('public.pem', 'wb') as f:
        f.write(pub)

def _sign():
    with open('private.key', 'rb') as f: 
        key = f.read()
    with open('payload.dat', 'rb') as f:
        payload = f.read()
    signature = sign(payload, key, password="ABC")
    with open('signature.sig', 'wb') as f:
        f.write(base64.b64encode(signature))

def _verify():
    with open('public.pem', 'rb') as f:
        pub = f.read()
    with open('payload.dat', 'rb') as f:
        payload = f.read()
    with open('signature.sig', 'rb') as f:
        signature = base64.b64decode(f.read())
    verify(payload, signature, pub)


def main():
    (key, pub) = generate_keypair(password="0123456")
    print(key)
    print(pub)
    payload = "ABCDEFG"
    signature = base64.b64encode(sign(payload, key, password="0123456"))
    print(signature)
    print(verify(payload, base64.b64decode(signature), pub))


if __name__ == "__main__":
    main()