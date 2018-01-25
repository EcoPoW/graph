import hashlib
import time
import random
import string

import tornado
import torndb


db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

certain_value = "00000"
certain_value = certain_value + 'f'*(64-len(certain_value))

target_prev_hash = '00000fabe6c7a87cd0bafa3561f98c6a790011227776bad974f4bff24a24c902'
target_nonce = 100000
target_prev_blocks = db.query("SELECT * FROM chain WHERE prev_hash = %s ORDER BY nonce", target_prev_hash)
if target_prev_blocks:
    target_nonce = target_prev_blocks[0].nonce
print(target_nonce)

while True:
    current_block_hash = 'f'*64
    # t1 = time.time()
    wallet_address = ''.join([random.choice(string.ascii_lowercase) for i in range(32)])

    for nonce in range(100000):
        block_hash = hashlib.sha256(("data" + target_prev_hash + str(wallet_address) + str(nonce)).encode('utf8')).hexdigest()
        # t2 = time.time()
        # if t2 - t1 >= 5:
        #     nonce = 0
        #     break

        if current_block_hash > block_hash and nonce < target_nonce:
            current_block_hash = block_hash
            if block_hash < certain_value:
                print(block_hash, nonce)
                db.execute("INSERT INTO chain (hash, prev_hash, nonce, wallet_address, data) VALUES (%s, %s, %s, %s, '')", block_hash, target_prev_hash, nonce, wallet_address)
                target_prev_hash = block_hash
                target_nonce = 100000
                break
    # print()

