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

from leader import lastest_block
from election import election

db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

certain_value = "0"
certain_value = certain_value + 'f'*(64-len(certain_value))

processed_txids = set()

def main(sk_filename):
    global processed_txids

    sk = SigningKey.from_pem(open(sk_filename).read())

    vk = sk.get_verifying_key()
    pk = str(base64.b64encode(vk.to_string()), encoding='utf8')

    timestamp = str(int(time.time()-300))
    leaders = db.query("SELECT * FROM leaders WHERE pk = %s AND timestamp > %s", pk, timestamp)

    if not leaders:
        election(sk_filename)
    else:
        # leader = leaders[0]

        transactions = db.query("SELECT * FROM transactions")
        random.shuffle(transactions)
        for transaction in transactions:
            if transaction.txid in processed_txids:
                continue
            processed_txids.add(transaction.txid)

            data = json.loads(transaction.data)
            sender = data["transaction"]["sender"]
            receiver = data["transaction"]["receiver"]
            amount = data["transaction"]["amount"]
            signature = data["signature"]

            chain_txids = set()
            sender_blocks = lastest_block(sender)
            receiver_blocks = lastest_block(receiver)
            for blockhash in set(sender_blocks+receiver_blocks):
                tx = db.get("SELECT * FROM graph WHERE hash = %s", blockhash)
                tx_data = json.loads(tx.data)
                txid = tx_data["transaction"]["txid"]
                chain_txids.add(txid)

            if transaction.txid in chain_txids:
                continue

            from_block = sender_blocks[-1] if sender_blocks else sender
            to_block = receiver_blocks[-1] if receiver_blocks else receiver


            # query from_block and to_block
            # get balance and calcuate
            # update transaction's from_block and to_block

            data["from_block"] = from_block
            data["to_block"] = to_block
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
                    print("tx", nonce, block_hash)
                    try:
                        # query if any node taken from_block or to_block
                        db.execute("INSERT INTO graph (hash, from_block, to_block, sender, receiver, nonce, data) VALUES (%s, %s, %s, %s, %s, %s, %s)", block_hash, from_block, to_block, sender, receiver, nonce, transaction.data)
                        # db.execute("INSERT INTO graph (hash, from_block, to_block, sender, receiver, nonce, data, transaction_id, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", block_hash, from_block, to_block, sender, receiver, nonce, transaction.data, transaction.id, int(time.time()))
                        processed_txids.add(txid)
                    except:
                        pass
                    break

if __name__ == '__main__':
    # print("leader", sys.argv[1])
    sk_filename = sys.argv[1]
    while True:
        # time.sleep(random.randint(1, 8))
        main(sk_filename)
