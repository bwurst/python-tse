import os.path
from ctypes import *
from wormtypes import *

class Worm:
    wormlib = None
    
    def __init__(self, mountpoint):
        self.wormlib = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))
        # FIXME: WormContext
        self.ctx = WormContext()
        # FIXME: worm_init()
        ret = self.wormlib.worm_init(self.ctx, mountpoint)
        print('return code for worm_init() => ', ret)

    def getVersion(self):
        self.wormlib.worm_getVersion.restype = c_char_p
        ret = self.wormlib.worm_getVersion()
        # liefert bytes
        return ret.decode('latin1')
        
    




