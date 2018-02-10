import sys
import hashlib
import random
import string
import base64
import time
import json

from ecdsa import SigningKey, VerifyingKey, NIST384p

import tornado
import torndb


db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

certain_value = "00000"
certain_value = certain_value + 'f'*(64-len(certain_value))

# 选举，由无限多个挖矿者众竞争出N个
# 由于网络延迟，可能有更多的挖矿者声称因为延迟，所以在deadline之后发来消息，但是署名timestamp是deadline之前，那么就会有分歧
# 比较比特币网络，挖出新区块并不意味着获得奖赏，还要依靠最长链法则才能完成竞争
# 所以选举依然是PoW

# 添加交易，一旦挖矿者被选举成功，它就有在一定时间内向系统写入交易的权限
# 这时候，N个挖矿者合作添加交易
# 这里选择PoL

def main():
    print("leader")
    sk_filename = sys.argv[1]
    sk = SigningKey.from_pem(open(sk_filename).read())

    vk = sk.get_verifying_key()
    pk = str(base64.b64encode(vk.to_string()), encoding='utf8')
    # print(pk)

    timestamp = str(int(time.time()-3600))
    leaders = db.query("SELECT * FROM leaders WHERE pk = %s AND timestamp > %s", pk, timestamp)
    # print(leaders)
    if not leaders:
        return
    # leader = leaders[0]

    transactions = db.query("SELECT * FROM transactions")
    for transaction in transactions:
        data = json.loads(transaction.data)
        sender = data["transaction"]["sender"]
        receiver = data["transaction"]["receiver"]
        from_node = data["transaction"]["from"]
        to_node = data["transaction"]["to"]
        amount = data["transaction"]["amount"]
        signature = data["signature"]

        # sk = SigningKey.generate(curve=NIST384p)
        # vk = sk.get_verifying_key()
        # vk_string = vk.to_string()
        # print(sender)
        vk2 = VerifyingKey.from_string(base64.b64decode(sender), curve=NIST384p)

        # print(json.dumps(data["transaction"]).encode('utf-8'))
        assert vk2.verify(base64.b64decode(signature), json.dumps(data["transaction"]).encode('utf-8'))

        # signature = sk.sign(json.dumps(transaction).encode('utf-8'))
        # data = {"transaction": transaction, "signature": str(base64.b64encode(signature), encoding="utf-8")}

        for nonce in range(100000000):
            block_hash = hashlib.sha256((transaction.data + from_node + to_node + pk + str(nonce)).encode('utf8')).hexdigest()
            if block_hash < certain_value:
                print(nonce, block_hash)
                db.execute("INSERT INTO graph (hash, from_node, to_node, nonce, data) VALUES (%s, %s, %s, %s, %s)", block_hash, from_node, to_node, nonce, transaction.data)
                break

if __name__ == '__main__':
    main()
