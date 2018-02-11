import sys
import base64
import time
import json
import uuid

from ecdsa import SigningKey, NIST384p
import torndb


db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

def main():
    sk_filename = sys.argv[1]
    sk = SigningKey.from_pem(open(sk_filename).read())

    receiver = sys.argv[2]
    # print(type(receiver))
    amount = float(sys.argv[3])

    vk = sk.get_verifying_key()
    sender = base64.b64encode(vk.to_string())
    txid = uuid.uuid4().hex
    timestamp = time.time()

    transaction = {
        "txid": txid,
        "sender": str(sender, encoding="utf-8"),
        "receiver": receiver,
        "timestamp": timestamp,
        "amount": amount
        }
    # print(json.dumps(transaction))

    signature = sk.sign(json.dumps(transaction).encode('utf-8'))
    data = {
        "transaction": transaction,
        "signature": str(base64.b64encode(signature), encoding="utf-8")
        }

    # try:
    assert vk.verify(signature, json.dumps(transaction).encode('utf-8'))
    db.execute("INSERT INTO transactions (data, txid, timestamp) VALUES (%s, %s, %s)", json.dumps(data), txid, int(timestamp))
    # except:
    #     pass


if __name__ == '__main__':
    main()
