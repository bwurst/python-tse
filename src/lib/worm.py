import os.path
from ctypes import *
from wormtypes import *
import config
import datetime
from worminfo import Worm_Info

def find_mountpoint():
    # Lese alle gemounteten Laufwerke
    with open('/proc/mounts', 'r') as mounts:
        # iteriere über die Laufwerke
        for line in mounts.readlines():
            dir = line.split(' ')[1]
            # Teste, ob die Datei vorhanden ist. Erster Treffer wird zurückgegeben.
            if os.path.exists(os.path.join(dir, 'TSE_COMM.DAT')):
                return dir
    return None


class Worm:
    wormlib = None

    def __init__(self, mountpoint = None):
        if not mountpoint:
            mountpoint = find_mountpoint()
        self.wormlib = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))

        self.ctx = WormContext()
        self.info = None

        self.wormlib.worm_init.restype = WormError
        self.wormlib.worm_init.argtypes = (POINTER(WormContext), c_char_p)
        ret = self.wormlib.worm_init(byref(self.ctx), mountpoint.encode('utf-8'))
        # FIXME: returncode auswerten
        print('return code for worm_init() => ', ret)
        
        self.info = Worm_Info(self)


    def __del__(self):
        if self.info:
            del(self.info)
        self.wormlib.worm_cleanup.restype = WormError
        ret = self.wormlib.worm_cleanup(self.ctx)
        # FIXME: returncode auswerten
        print('return code for worm_cleanup() => ', ret)

    ####################################################################
    # Library Information
    ####################################################################

    def getVersion(self):
        self.wormlib.worm_getVersion.restype = c_char_p
        ret = self.wormlib.worm_getVersion()
        # liefert bytes. Wir konvertieren als latin1, da es da keine UnicodeDecodeErrors geben kann.
        return ret.decode('latin1')


    def signatureAlgorithm(self):
        self.wormlib.worm_signatureAlgorithm.restype = c_char_p
        ret = self.wormlib.worm_signatureAlgorithm()
        return ret.decode('utf-8')

    ####################################################################
    # TSE-Configuration
    ####################################################################
    
    def tse_factoryReset(self):
        self.wormlib.worm_tse_factoryReset.restype = WormError
        self.wormlib.worm_tse_factoryReset.argtypes = (WormContext, )
        ret = self.wormlib.worm_tse_factoryReset(self.ctx)
        # FIXME: Error handling
        return ret
    
    def tse_runSelfTest(self):
        clientId = c_wchar_p(config.clientId)
        #print('clientId:', clientId.value)
        self.wormlib.worm_tse_runSelfTest.argtypes = (WormContext, c_wchar_p)
        self.wormlib.worm_tse_runSelfTest.restype = WormError
        ret = self.wormlib.worm_tse_runSelfTest(self.ctx, clientId)

        print('ret:', ret)
        
        
    def user_login(self):
        WormUserId = WORM_USER_TIME_ADMIN # WORM_USER_ADMIN
        pin = c_wchar_p(config.PIN_TIME_ADMIN)
        pinLength = 5
        remainingRetries = c_int()
        
        self.wormlib.worm_user_login.argtypes = (self.type_ctx, c_int, c_wchar_p, c_int, c_int)
        self.wormlib.worm_user_login.restype = WormError
        ret = self.wormlib.worm_user_login(self.ctx, WormUserId, pin, pinLength, remainingRetries)

        print('remainingRetries: ', remainingRetries.value)
        print(ret)
        return ret
        
        
    def user_unblock(self):
        WormUserId = WORM_USER_TIME_ADMIN
        puk = c_wchar_p(config.PUK)
        pukLength = 6 
        newPin = c_wchar_p(config.PIN_TIME_ADMIN)
        newPinLength = 5
        remainingRetries = c_int()
        
        self.wormlib.worm_user_unblock.argtypes = (self.type_ctx, c_int, c_wchar_p, c_int, c_wchar_p, c_int, c_int)
        self.wormlib.worm_user_unblock.restype = WormError
        ret = self.wormlib.worm_user_unblock(self.ctx, WormUserId, puk, pukLength, newPin, newPinLength, remainingRetries)

        print('remainingRetries: ', remainingRetries.value)
        print(ret)
        return ret
        
        
    def user_change_puk(self):
        puk = c_wchar_p(config.PUK)
        pukLength = 6
        newPuk = c_wchar_p(config.PUK) # FIXME: das sollte eigentlich ein andere PUK sein, als der erste :)
        newPukLength = 6
        remainingRetries = c_int()
        
        self.wormlib.worm_user_change_puk.argtypes = (self.type_ctx,  c_wchar_p, c_int, c_wchar_p, c_int, POINTER(c_int))
        self.wormlib.worm_user_change_puk.restype = WormError
        ret = self.wormlib.worm_user_change_puk(self.ctx, puk, pukLength, newPuk, newPukLength, byref(remainingRetries))
        print('remainingRetries: ', remainingRetries.value)
        print(ret)
        

    def flash_health_summary(self):
        uncorrectableEccErrors = c_uint32()
        percentageRemainingSpareBlocks = c_uint8()
        percentageRemainingEraseCounts = c_uint8()
        percentageRemainingTenYearsDataRetention = c_uint8()

        self.wormlib.worm_flash_health_summary.argtypes = (self.ctx, POINTER(c_uint32), POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint8))
        self.wormlib.worm_flash_health_summary.restype = WormError
        ret = self.wormlib.worm_flash_health_summary(self.ctx, byref(uncorrectableEccErrors), byref(percentageRemainingSpareBlocks),
                                                      byref(percentageRemainingEraseCounts), byref(percentageRemainingTenYearsDataRetention))

        print(ret)
        print(uncorrectableEccErrors.value)
        print(percentageRemainingSpareBlocks.value)
        print(percentageRemainingEraseCounts.value)
        print(percentageRemainingTenYearsDataRetention.value)

