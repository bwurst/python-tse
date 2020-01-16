import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))

from worm import Worm

if len(sys.argv) < 2:
    print('usage: %s <mountpoint>' % (sys.argv[0],))
    sys.exit()

mountpoint = sys.argv[1]
worm = Worm(mountpoint)

print(worm.getVersion())


