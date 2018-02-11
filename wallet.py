import sys
import base64
from ecdsa import SigningKey, NIST384p

# generate key
# sk = SigningKey.generate(curve=NIST384p)
# open("pk.pem", "w").write(str(sk.to_pem(), encoding="utf-8"))


sk_filename = sys.argv[1]
sk = SigningKey.from_pem(open(sk_filename).read())

vk = sk.get_verifying_key()
print(str(base64.b64encode(vk.to_string()), encoding='utf-8'))
# signature = sk.sign(b"message")
# print(base64.b64encode(signature))
# assert vk.verify(signature, b"message")
