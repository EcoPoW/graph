import sys
import hashlib
import random
import string
import base64

from ecdsa import SigningKey, NIST384p

import tornado
import torndb


db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

certain_value = "000000"
certain_value = certain_value + 'f'*(64-len(certain_value))

# 选举，由无限多个挖矿者众竞争出N个
# 由于网络延迟，可能有更多的挖矿者声称因为延迟，所以在deadline之后发来消息，但是署名timestamp是deadline之前，那么就会有分歧
# 比较比特币网络，挖出新区块并不意味着获得奖赏，还要依靠最长链法则才能完成竞争
# 所以选举依然是PoW

# 添加交易，一旦挖矿者被选举成功，它就有在一定时间内向系统写入交易的权限
# 这时候，N个挖矿者合作添加交易
# 这里选择PoL

def main():
    print("election")
    sk_filename = sys.argv[1]
    sk = SigningKey.from_pem(open(sk_filename).read())

    vk = sk.get_verifying_key()
    wallet_address = str(base64.b64encode(vk.to_string()), encoding='utf8')
    print(wallet_address)
    prev_hash = "0" * 64

    nonce = 0
    while True:
        block_hash = hashlib.sha256(('last.data' + prev_hash + wallet_address + str(nonce)).encode('utf8')).hexdigest()
        if block_hash < certain_value:
            print(block_hash, nonce)
            # db.execute("INSERT INTO chain (hash, prev_hash, nonce, wallet_address, data) VALUES (%s, %s, %s, %s, '')", block_hash, longest_hash, nonce, wallet_address)
            break
        nonce += 1

if __name__ == '__main__':
    main()
