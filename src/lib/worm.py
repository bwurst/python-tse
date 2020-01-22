import os.path
from ctypes import *
from wormtypes import *
import config


class Worm:
    wormlib = None


    def __init__(self, mountpoint):
        self.wormlib = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))

        #self.ctx = c_void_p()
        #self.ctx = pointer(c_void_p())
        #self.ctx = pointer(c_int())
        #self.ctx = byref(c_int())
        
        ctx_struct = WormContext()
        self.ctx = pointer(ctx_struct)
        print('WormContext vor init: ', self.ctx)

        #self.type_ctx = c_void_p
        #self.type_ctx = type(self.ctx)
                
        self.type_ctx_struct = WormContext # wird nicht benötigt...
        self.type_ctx = POINTER(type(self.ctx))
        
        self.wormlib.worm_init.restype = WormError
        self.wormlib.worm_init.argtypes = (self.type_ctx, c_char_p)
        ret = self.wormlib.worm_init(self.ctx, mountpoint.encode('utf-8'))
        print('WormContext after init: ', self.ctx) # wenn ich die Doku verstanden habe, dann müsste sich der Wert eigentlich geändert haben
        # FIXME: returncode auswerten
        print('return code for worm_init() => ', ret)


    def __del__(self):
        self.wormlib.worm_cleanup.argtypes = (self.type_ctx,)
        self.wormlib.worm_cleanup.restype = WormError
        print('ok bis vor worm_cleanup')
        ret = self.wormlib.worm_cleanup(self.ctx)
        print('ok bis nach worm_cleanup')
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
        self.wormlib.worm_info_new.argtypes = (self.type_ctx,)
        self.wormlib.worm_info_new.restype = WormInfo
        self.info = self.wormlib.worm_info_new(self.ctx)


    def __info_free(self):
        self.wormlib.worm_info_free.argtypes = (WormInfo,)
        self.wormlib.worm_info_free.restype = c_void_p
        self.wormlib.worm_info_free(self.info)


    def info_read(self):
        self.__info_new()

        self.wormlib.worm_info_read.argtypes = (WormInfo,)
        self.wormlib.worm_info_read.restype = WormInfo  # und nicht WormError (wie in der API-Spec)
        self.wormlib.worm_info_read(self.info)

        print('isDevelopmentFirmware: ', self.info.isDevelopmentFirmware)
        print('hasChangedPuk: ', self.info.hasChangedPuk)
        print('hasValidTime: ', self.info.hasValidTime)
        print('isExportEnabledIfCspTestFails: ', self.info.isExportEnabledIfCspTestFails)

        print('maxRegisteredClients: ', self.info.maxRegisteredClients)
        print('registeredClients: ', self.info.registeredClients)

        # print('tseDescription: ', self.info.tseDescription)
        print('size: ', self.info.size)
        print('capacity: ', self.info.capacity)
        print('timeUntilNextSelfTest: ', self.info.timeUntilNextSelfTest)
        print('initializationState: ', self.info.initializationState)
        print('tsePublicKey: ', self.info.tsePublicKey)
        print('tseSerialNumber: ', self.info.tseSerialNumber)
        print('certificateExpirationDate: ', self.info.certificateExpirationDate)

        self.__info_free()


    def info_capacity(self):
        self.__info_new()
        
        self.wormlib.worm_info_capacity.argtypes = (WormInfo, )
        self.wormlib.worm_info_capacity.restype = c_uint32
        ret = self.wormlib.worm_info_capacity(self.info)
        print(ret)

        
    def runSelfTest(self):
        clientId = c_wchar_p(config.clientId)
        #print('clientId:', clientId.value)
        
        self.wormlib.worm_tse_runSelfTest.argtypes = (self.type_ctx, c_wchar_p)
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

