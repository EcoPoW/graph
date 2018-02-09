import hashlib
import random
import string

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
    # longest = longest_chain()
    # print(longest)
    # longest_hash = longest[-1]

    # last = db.get("SELECT * FROM chain WHERE hash = '' AND prev_hash = '-' ORDER BY id ASC LIMIT 1")
    # if not last:
    #     print("No tx to pack")
    #     return

    # wallet_address = ''.join([random.choice(string.ascii_lowercase) for i in range(32)])
    # for wallet_address in wallet_addresses:
    for nonce in range(100000):
        block_hash = hashlib.sha256(('last.data' + longest_hash + wallet_address + str(nonce)).encode('utf8')).hexdigest()
        if block_hash < certain_value:
            print(nonce, block_hash)
            # db.execute("UPDATE chain SET hash = %s, prev_hash = %s, nonce = %s, wallet_address = %s WHERE id = %s", block_hash, longest_hash, nonce, wallet_address, last.id)
            db.execute("INSERT INTO chain (hash, prev_hash, nonce, wallet_address, data) VALUES (%s, %s, %s, %s, '')", block_hash, longest_hash, nonce, wallet_address)
            break

if __name__ == '__main__':
    main()
