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

processed_txids = set()

# 选举，由无限多个挖矿者众竞争出N个
# 由于网络延迟，可能有更多的挖矿者声称因为延迟，所以在deadline之后发来消息，但是署名timestamp是deadline之前，那么就会有分歧
# 比较比特币网络，挖出新区块并不意味着获得奖赏，还要依靠最长链法则才能完成竞争
# 所以选举依然是PoW

# 添加交易，一旦挖矿者被选举成功，它就有在一定时间内向系统写入交易的权限
# 这时候，N个挖矿者合作添加交易
# 这里选择PoL

def longest_chain(root_hash = '0'*64):
    roots = db.query("SELECT * FROM graph WHERE from_node = %s OR to_node = %s ORDER BY nonce", root_hash, root_hash)

    chains = []
    prev_hashs = []
    for root in roots:
        # print(root.id)
        chains.append([root.hash])
        prev_hashs.append(root.hash)

    while True:
        if prev_hashs:
            prev_hash = prev_hashs.pop(0)
        else:
            break

        leaves = db.query("SELECT * FROM graph WHERE from_node = %s OR to_node = %s ORDER BY nonce", prev_hash, prev_hash)
        if len(leaves) > 0:
            for leaf in leaves:
                # print(leaf)
                for c in chains:
                    if c[-1] == prev_hash:
                        chain = c.copy()
                        chain.append(leaf.hash)
                        chains.append(chain)
                        break
                if leaf.hash not in prev_hashs and leaf.hash:
                    prev_hashs.append(leaf.hash)

    longest = None
    for i in chains:
        # print(i)
        if not longest:
            longest = i
        if len(longest) < len(i):
            longest = i
    return longest

def main():
    global processed_txids

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
        if transaction.txid in processed_txids:
            continue

        data = json.loads(transaction.data)
        sender = data["transaction"]["sender"]
        receiver = data["transaction"]["receiver"]
        # from_node = data["transaction"]["from"]
        # to_node = data["transaction"]["to"]
        amount = data["transaction"]["amount"]
        signature = data["signature"]

        sender_nodes = longest_chain(sender)
        receiver_nodes = longest_chain(receiver)
        from_node = sender_nodes[-1] if sender_nodes else sender
        to_node = receiver_nodes[-1] if receiver_nodes else receiver

        data["from_node"] = from_node
        data["to_node"] = to_node
        data["sender_balance"] = ""
        data["receiver_balance"] = ""
        data["leader_publickey"] = pk

        vk2 = VerifyingKey.from_string(base64.b64decode(sender), curve=NIST384p)
        assert vk2.verify(base64.b64decode(signature), json.dumps(data["transaction"]).encode('utf-8'))

        # signature = sk.sign(json.dumps(transaction).encode('utf-8'))
        # data = {"transaction": transaction, "signature": str(base64.b64encode(signature), encoding="utf-8")}

        for nonce in range(100000000):
            block_hash = hashlib.sha256((json.dumps(data) + pk + str(nonce)).encode('utf8')).hexdigest()
            if block_hash < certain_value:
                print(nonce, block_hash)
                try:
                    db.execute("INSERT INTO graph (hash, from_node, to_node, nonce, data) VALUES (%s, %s, %s, %s, %s)", block_hash, from_node, to_node, nonce, transaction.data)
                    processed_txids.add(transaction.txid)
                except:
                    pass
                break

if __name__ == '__main__':
    print("leader", sys.argv[1])
    while True:
        main()
        time.sleep(5)