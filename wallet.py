import base64
from ecdsa import SigningKey, NIST384p

# generate key
# sk = SigningKey.generate(curve=NIST384p)
# open("pk.pem","w").write(str(sk.to_pem(), encoding="utf-8"))


sk = SigningKey.from_pem(open("pk.pem").read())
# print(sk)
vk = sk.get_verifying_key()
print(base64.b64encode(vk.to_string()))
signature = sk.sign(b"message message message message message")
print(base64.b64encode(signature))
assert vk.verify(signature, b"message")