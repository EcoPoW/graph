import sys
import base64
import time
import json

from ecdsa import SigningKey, NIST384p
import torndb


db = torndb.Connection("127.0.0.1", "test", user="root", password="root")


def longest_chain(root_hash = '0'*64):
    roots = db.query("SELECT * FROM graph WHERE hash = %s ORDER BY nonce", root_hash)

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
    sk_filename = sys.argv[1]
    sk = SigningKey.from_pem(open(sk_filename).read())

    receiver = sys.argv[2]
    # print(type(receiver))
    amount = float(sys.argv[3])

    vk = sk.get_verifying_key()
    sender = base64.b64encode(vk.to_string())
    sender_nodes = longest_chain(sender)
    receiver_nodes = longest_chain(receiver)

    transaction = {
        "sender": str(sender, encoding="utf-8"),
        "receiver": receiver,
        "from": sender_nodes[-1],
        "to": receiver_nodes[-1],
        "timestamp": time.time(),
        "amount": amount
        }
    # print(json.dumps(transaction))

    signature = sk.sign(json.dumps(transaction).encode('utf-8'))
    data = {
        "transaction": transaction, 
        "signature": str(base64.b64encode(signature), encoding="utf-8")
        }
    assert vk.verify(signature, json.dumps(transaction).encode('utf-8'))

    db.execute("INSERT INTO transactions (data, from_node, to_node) VALUES (%s, %s, %s)", json.dumps(data), sender_nodes[-1], receiver_nodes[-1])


if __name__ == '__main__':
    main()
