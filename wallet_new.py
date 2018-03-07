import sys
import base64
from ecdsa import SigningKey, NIST384p

sk_filename = sys.argv[1]

# generate key
sk = SigningKey.generate(curve=NIST384p)
open(sk_filename, "w").write(str(sk.to_pem(), encoding="utf-8"))

vk = sk.get_verifying_key()
print(str(base64.b64encode(vk.to_string()), encoding="utf-8"))
