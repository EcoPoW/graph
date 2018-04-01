import sys

import signal
import subprocess

leaders = set()
def signal_handler(signal, frame):
    global leaders
    for l in leaders:
        # l.terminate()
        l.kill()
    print('Pressed Ctrl+C!')
    sys.exit(0)

total = sys.argv[1]
for i in range(1,int(total)+1):
    print(i)
    p = subprocess.Popen(['python', 'leader_auto.py', 'p%s.pem'%i], shell=False)
    leaders.add(p)


signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')
signal.pause()
