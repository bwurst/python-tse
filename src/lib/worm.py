import os.path
from ctypes import *
from wormtypes import *

class Worm:
    wormlib = None
    
    def __init__(self, mountpoint):
        self.wormlib = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))
        self.ctx = WormContext()
        self.wormlib.worm_init.argtypes = (WormContext, c_char_p)
        self.wormlib.worm_init.restype = WormError
        ret = self.wormlib.worm_init(self.ctx, mountpoint.encode('utf-8'))
        # FIXME: returncode auswerten
        print('return code for worm_init() => ', ret)


    def __del__(self):
        self.wormlib.worm_cleanup.argtypes = (WormContext,)
        self.wormlib.worm_cleanup.restype = WormError
        ret = self.wormlib.worm_cleanup(self.ctx)
        # FIXME: returncode auswerten
        print('return code for worm_cleanup() => ', ret)


    def getVersion(self):
        self.wormlib.worm_getVersion.restype = c_char_p
        ret = self.wormlib.worm_getVersion()
        # liefert bytes. Wir konvertieren als latin1, da es da keine UnicodeDecodeErrors geben kann.
        return ret.decode('latin1')
        
    




