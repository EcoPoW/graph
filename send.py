import sys
import base64
import json

from ecdsa import SigningKey, NIST384p
import torndb


db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

# generate key
# sk = SigningKey.generate(curve=NIST384p)
# open("pk.pem","w").write(str(sk.to_pem(), encoding="utf-8"))


sk_filename = sys.argv[1]
sk = SigningKey.from_pem(open(sk_filename).read())

receiver = sys.argv[2]
# print(type(receiver))
amount = float(sys.argv[3])

vk = sk.get_verifying_key()
sender = base64.b64encode(vk.to_string())
transaction = {"sender": str(sender, encoding="utf-8"), "receiver": receiver, "from": "", "to": "", "amount": amount}
# print(json.dumps(transaction))

signature = sk.sign(json.dumps(transaction).encode('utf-8'))
data = {"transaction": transaction, "signature": str(base64.b64encode(signature), encoding="utf-8")}
assert vk.verify(signature, json.dumps(transaction).encode('utf-8'))

db.execute("INSERT INTO transactions (data, from_node, to_node) VALUES (%s, %s, %s)", json.dumps(data), str(sender, encoding="utf-8"), receiver)

