import sys
import hashlib
import random
import string
import base64
import time

from ecdsa import SigningKey, NIST384p

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

def longest_chain(root_hash = '0'*64):
    roots = db.query("SELECT * FROM leaders WHERE prev_hash = %s ORDER BY nonce", root_hash)

    chains = []
    prev_hashs = []
    for root in roots:
        chains.append([root.hash])
        prev_hashs.append(root.hash)

    while True:
        if prev_hashs:
            prev_hash = prev_hashs.pop(0)
        else:
            break

        leaves = db.query("SELECT * FROM leaders WHERE prev_hash = %s ORDER BY nonce", prev_hash)
        if len(leaves) > 0:
            for leaf in leaves:
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


def election(sk_filename):
    print("election")
    sk = SigningKey.from_pem(open(sk_filename).read())

    vk = sk.get_verifying_key()
    pk = str(base64.b64encode(vk.to_string()), encoding='utf8')
    print(pk)

    longest = longest_chain()
    prev_hash = longest[-1] if longest else "0"*64

    nonce = 0
    while True:
        timestamp = str(int(time.time()))
        block_hash = hashlib.sha256((prev_hash + pk + timestamp + str(nonce)).encode('utf8')).hexdigest()
        if block_hash < certain_value:
            print("election", nonce, block_hash)
            db.execute("INSERT INTO leaders (hash, prev_hash, nonce, pk, timestamp) VALUES (%s, %s, %s, %s, %s)", block_hash, prev_hash, nonce, pk, timestamp)
            break
        nonce += 1


if __name__ == '__main__':
    sk_filename = sys.argv[1]
    election(sk_filename)
