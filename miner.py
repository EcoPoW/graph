import hashlib
import random
import string

import tornado
import torndb

wallet_addresses = '''qlyqqkweqnvwinmirrolmdcjtxgqnjgz
uuexdxyrckhexaipuvyzjgjjaeuipztp
vaftdkccdqdyxtmikepazqsutzzvsrac
ofmeuvfjsetsxtmjcpdbnziewkyojaxe
vtozwatpfkcfpplvbcwusewafsrgtbtc
xjhoiulckhexjvqjhoqxukamfckwxjfd
vtlqopzzbagrobomrunnmjcnvuglgewk
ruvddqddtfbhgvbempfffokgzqgowlos
zarjdkmzdeyxterakhpotmrebrypzrri
nfxpbjoilazspqhstglyairflknwmwln
lhudoyigbgoermwpzxoxcufbqrgmbjno
jbrotipuakwtheibztfrpvuawaylrnsf
odejbhcmunwfuenerdjxiimtnctkfjkb
fujnwypzclqegnnrsmvmfvdfawnehkpl
rhpopnpsntuifmukvsobnalnxrugxwde
wukcvewiwsmtvbzerljziefgbepxmumi
wvdhwyxqcmpneamysqwaplakjwtsynvv
bsuosyexdsvrxhxjntoqqvvqqvmrihfe'''.split('\n')

db = torndb.Connection("127.0.0.1", "test", user="root", password="root")

certain_value = "00000"
certain_value = certain_value + 'f'*(64-len(certain_value))

# TODO, more than one longest chain
def longest_chain(root_hash = '0'*64):
    roots = db.query("SELECT * FROM chain WHERE prev_hash = %s ORDER BY nonce", root_hash)

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

        leaves = db.query("SELECT * FROM chain WHERE prev_hash = %s ORDER BY nonce", prev_hash)
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
        print(i)
        if not longest:
            longest = i
        if len(longest) < len(i):
            longest = i
    return longest

def main():
    longest = longest_chain()
    print(longest)
    longest_hash = longest[-1]

    # last = db.get("SELECT * FROM chain WHERE hash = '' AND prev_hash = '-' ORDER BY id ASC LIMIT 1")
    # if not last:
    #     print("No tx to pack")
    #     return

    # wallet_address = ''.join([random.choice(string.ascii_lowercase) for i in range(32)])
    for wallet_address in wallet_addresses:
        for nonce in range(100000):
            block_hash = hashlib.sha256(('last.data' + longest_hash + wallet_address + str(nonce)).encode('utf8')).hexdigest()
            if block_hash < certain_value:
                print(nonce, block_hash)
                # db.execute("UPDATE chain SET hash = %s, prev_hash = %s, nonce = %s, wallet_address = %s WHERE id = %s", block_hash, longest_hash, nonce, wallet_address, last.id)
                db.execute("INSERT INTO chain (hash, prev_hash, nonce, wallet_address, data) VALUES (%s, %s, %s, %s, '')", block_hash, longest_hash, nonce, wallet_address)
                break

if __name__ == '__main__':
    main()
