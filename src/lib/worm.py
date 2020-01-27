import os.path
from ctypes import *
from wormtypes import *
import config


class Worm:
    wormlib = None


    def __init__(self, mountpoint):
        self.wormlib = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))

        self.ctx = WormContext()
        self.info = None

        self.wormlib.worm_init.restype = WormError
        self.wormlib.worm_init.argtypes = (POINTER(WormContext), c_char_p)
        ret = self.wormlib.worm_init(byref(self.ctx), mountpoint.encode('utf-8'))
        # FIXME: returncode auswerten
        print('return code for worm_init() => ', ret)


    def __del__(self):
        self.wormlib.worm_cleanup.restype = WormError
        ret = self.wormlib.worm_cleanup(self.ctx)
        # FIXME: returncode auswerten
        print('return code for worm_cleanup() => ', ret)


    def getVersion(self):
        self.wormlib.worm_getVersion.restype = c_char_p
        ret = self.wormlib.worm_getVersion()
        # liefert bytes. Wir konvertieren als latin1, da es da keine UnicodeDecodeErrors geben kann.
        return ret.decode('latin1')


    def signatureAlgorithm(self):
        self.wormlib.worm_signatureAlgorithm.restype = c_char_p
        ret = self.wormlib.worm_signatureAlgorithm()
        return ret.decode('utf-8')


    def __info_new(self):
        self.wormlib.worm_info_new.argtypes = (WormContext,)
        self.wormlib.worm_info_new.restype = WormInfo
        self.info = cast(self.wormlib.worm_info_new(self.ctx), WormInfo)


    def __info_free(self):
        self.wormlib.worm_info_free(byref(self.info))


    def info_read(self):
        if not self.info:
            self.__info_new()

        self.wormlib.worm_info_read.restype = WormError
        self.wormlib.worm_info_read.argtypes = (WormInfo, )
        ret = self.wormlib.worm_info_read(self.info)

        #print('isDevelopmentFirmware: ', self.info.isDevelopmentFirmware)
        #print('hasChangedPuk: ', self.info.hasChangedPuk)
        #print('hasValidTime: ', self.info.hasValidTime)
        #print('isExportEnabledIfCspTestFails: ', self.info.isExportEnabledIfCspTestFails)

        #print('maxRegisteredClients: ', self.info.maxRegisteredClients)
        #print('registeredClients: ', self.info.registeredClients)

        # print('tseDescription: ', self.info.tseDescription)
        #print('size: ', self.info.size)
        #print('capacity: ', self.info.capacity)
        #print('timeUntilNextSelfTest: ', self.info.timeUntilNextSelfTest)
        #print('initializationState: ', self.info.initializationState)
        #print('tsePublicKey: ', self.info.tsePublicKey)
        #print('tseSerialNumber: ', self.info.tseSerialNumber)
        #print('certificateExpirationDate: ', self.info.certificateExpirationDate)

        #self.__info_free()


    def info_capacity(self):
        self.wormlib.worm_info_capacity.restype = c_uint64
        ret = self.wormlib.worm_info_capacity(self.info)
        return ret

    def info_isDevelopmentFirmware(self):
        self.wormlib.worm_info_isDevelopmentFirmware.restype = c_uint64
        self.wormlib.worm_info_isDevelopmentFirmware.argtypes = (WormInfo,)
        ret = self.wormlib.worm_info_isDevelopmentFirmware(self.info)
        return bool(ret)

    def info_size(self):
        self.wormlib.worm_info_size.restype = c_uint64
        self.wormlib.worm_info_size.argtypes = (WormInfo,)
        ret = self.wormlib.worm_info_size(self.info)
        return ret
        
    def info_hasValidTime(self):
        self.wormlib.worm_info_hasValidTime.restype = c_uint64
        self.wormlib.worm_info_hasValidTime.argtypes = (WormInfo,)
        ret = self.wormlib.worm_info_hasValidTime(self.info)
        return bool(ret)
        
    def info_hasPassedSelfTest(self):
        self.wormlib.worm_info_hasPassedSelfTest.restype = c_uint64
        self.wormlib.worm_info_hasPassedSelfTest.argtypes = (WormInfo,)
        ret = self.wormlib.worm_info_hasPassedSelfTest(self.info)
        return bool(ret)
        
    def info_isCtssInterfaceActive(self):
        self.wormlib.worm_info_isCtssInterfaceActive.restype = c_uint64
        self.wormlib.worm_info_isCtssInterfaceActive.argtypes = (WormInfo,)
        ret = self.wormlib.worm_info_isCtssInterfaceActive(self.info)
        return bool(ret)
        
        
    def runSelfTest(self):
        clientId = c_wchar_p(config.clientId)
        #print('clientId:', clientId.value)
        
        self.wormlib.worm_tse_runSelfTest.argtypes = (c_void_p, c_wchar_p)
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
        
        self.wormlib.worm_user_change_puk.argtypes = (self.type_ctx,  c_wchar_p, c_int, c_wchar_p, c_int, c_int)
        self.wormlib.worm_user_change_puk.restype = WormError
        ret = self.wormlib.worm_user_change_puk(self.ctx, puk, pukLength, newPuk, newPukLength, remainingRetries)

        print('remainingRetries: ', remainingRetries.value)
        print(ret)
        

    def flash_health_summary(self):
        uncorrectableEccErrors = c_uint32()
        percentageRemainingSpareBlocks = c_uint8()
        percentageRemainingEraseCounts = c_uint8()
        percentageRemainingTenYearsDataRetention = c_uint8()

        self.wormlib.worm_flash_health_summary.argtypes = (self.type_ctx, c_uint32, c_uint8, c_uint8, c_uint8)
        self.wormlib.worm_flash_health_summary.restype = WormError

        ret = self.wormlib.worm_flash_health_summary(self.ctx, uncorrectableEccErrors, percentageRemainingSpareBlocks,
                                                      percentageRemainingEraseCounts, percentageRemainingTenYearsDataRetention)

        print(ret)
        print(uncorrectableEccErrors)
        print(percentageRemainingSpareBlocks)
        print(percentageRemainingEraseCounts)
        print(percentageRemainingTenYearsDataRetention)

