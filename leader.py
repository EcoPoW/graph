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

certain_value = "0"
certain_value = certain_value + 'f'*(64-len(certain_value))


# 添加交易，一旦挖矿者被选举成功，它就有在一定时间内向系统写入交易的权限
# 这时候，m个挖矿者合作添加交易
# 这里选择PoL
# 优先选择最长链，如果两个一样长，选择nonce小的

def lastest_block(root_hash):
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

        leaves = db.query("SELECT * FROM graph WHERE from_node = %s AND sender = %s ORDER BY nonce", prev_hash, root_hash)
        if len(leaves) > 0:
            for leaf in leaves:
                # print(leaf.id)
                for c in chains:
                    if c[-1] == prev_hash:
                        chain = c.copy()
                        chain.append(leaf.hash)
                        chains.append(chain)
                        break
                if leaf.hash not in prev_hashs and leaf.hash:
                    prev_hashs.append(leaf.hash)

        leaves = db.query("SELECT * FROM graph WHERE to_node = %s AND receiver = %s ORDER BY nonce", prev_hash, root_hash)
        if len(leaves) > 0:
            for leaf in leaves:
                # print(leaf.id)
                for c in chains:
                    if c[-1] == prev_hash:
                        chain = c.copy()
                        chain.append(leaf.hash)
                        chains.append(chain)
                        break
                if leaf.hash not in prev_hashs and leaf.hash:
                    prev_hashs.append(leaf.hash)

    longest = []
    for i in chains:
        if not longest:
            longest = i
        if len(longest) < len(i):
            longest = i
    # print(longest)
    return longest

def main():
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
        processed_txids = set()

        data = json.loads(transaction.data)
        sender = data["transaction"]["sender"]
        receiver = data["transaction"]["receiver"]
        amount = data["transaction"]["amount"]
        signature = data["signature"]

        sender_nodes = lastest_block(sender)
        receiver_nodes = lastest_block(receiver)
        for node in sender_nodes+receiver_nodes:
            tx = db.get("SELECT * FROM graph WHERE hash = %s", node)
            tx_data = json.loads(tx.data)
            txid = tx_data["transaction"]["txid"]
            processed_txids.add(txid)

        from_node = sender_nodes[-1] if sender_nodes else sender
        to_node = receiver_nodes[-1] if receiver_nodes else receiver

        # print(processed_txids)
        if transaction.txid in processed_txids:
            continue

        # query from_node and to_node
        # get balance and calcuate
        # update transaction's from_node and to_node

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
                    # query if any node taken from_node or to_node
                    db.execute("INSERT INTO graph (hash, from_node, to_node, sender, receiver, nonce, data) VALUES (%s, %s, %s, %s, %s, %s, %s)", block_hash, from_node, to_node, sender, receiver, nonce, transaction.data)
                except:
                    pass
                break

if __name__ == '__main__':
    print("leader", sys.argv[1])
    while True:
        main()
        time.sleep(5)