import os.path
from ctypes import *
from wormtypes import *


class Worm:
    wormlib = None


    def __init__(self, mountpoint):
        self.wormlib = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))

        self.ctx = byref(c_int())

        # so gehts auch, ist aber angeblich viel langsamer:
        # self.ctx = pointer(c_int())

        self.wormlib.worm_init.argtypes = (WormContext, c_char_p)
        self.wormlib.worm_init.restype = WormError
        ret = self.wormlib.worm_init(self.ctx, mountpoint.encode('utf-8'))
        # FIXME: returncode auswerten
        print('return code for worm_init() => ', ret)


    def __del__(self):
        self.wormlib.worm_cleanup.argtypes = (WormContext,)
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
        self.wormlib.worm_info_new.argtypes = (WormContext,)
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
        self.wormlib.worm_info_capacity.argtypes = (c_void_p, )
        self.wormlib.worm_info_capacity.restype = c_uint32
        res = self.wormlib.worm_info_capacity(self.ctx)
        print(res)


    def flash_health_summary(self):
        uncorrectableEccErrors = c_uint32()
        percentageRemainingSpareBlocks = c_uint8()
        percentageRemainingEraseCounts = c_uint8()
        percentageRemainingTenYearsDataRetention = c_uint8()

        self.wormlib.worm_flash_health_summary.argtypes = (c_void_p, c_uint32, c_uint8, c_uint8, c_uint8)
        self.wormlib.worm_flash_health_summary.restype = WormError

        res = self.wormlib.worm_flash_health_summary(self.ctx, uncorrectableEccErrors, percentageRemainingSpareBlocks,
                                                      percentageRemainingEraseCounts, percentageRemainingTenYearsDataRetention)

        print(res)
        print(uncorrectableEccErrors)
        print(percentageRemainingSpareBlocks)
        print(percentageRemainingEraseCounts)
        print(percentageRemainingTenYearsDataRetention)

