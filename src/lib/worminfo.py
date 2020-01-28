import datetime
from ctypes import *
from wormtypes import *


class Worm_Info:
    def __init__(self, worm):
        self.ctx = worm.ctx
        self.wormlib = worm.wormlib

        self.wormlib.worm_info_new.argtypes = (WormContext,)
        self.wormlib.worm_info_new.restype = WormInfo
        self.info = cast(self.wormlib.worm_info_new(self.ctx), WormInfo)
        self.wormlib.worm_info_read.restype = WormError
        self.wormlib.worm_info_read.argtypes = (WormInfo, )
        self.update()
        
    def update(self):
        ret = self.wormlib.worm_info_read(self.info)
        # FIXME: Error handling


    def __del__(self):
        if self.info:
            self.wormlib.worm_info_free(self.info)
            self.info = None

    def __getattr__(self, key):
        if key in ['isDevelopmentFirmware', 'isStoreOpen', 'hasValidTime', 'hasPassedSelfTest', 
                   'isCtssInterfaceActive', 'isErsInterfaceActive', 'isExportEnabledIfCspTestFails',
                   'isDataImportInProgress', 'isTransactionInProgress', 'hasChangedPuk', 'hasChangedAdminPin',
                   'hasChangedTimeAdminPin']:
            return bool(self.__get_info_uint64(key))
        elif key in ['size', 'capacity', 'timeUntilNextSelfTest', 'startedTransactions', 'maxStartedTransactions',
                     'createdSignatures', 'maxSignatures', 'remainingSignatures', 'maxTimeSynchronizationDelay',
                     'maxUpdateDelay', 'registeredClients', 'maxRegisteredClients', 'tarExportSizeInSectors',
                     'tarExportSize', 'initializationState']:
            return self.__get_info_uint64(key)
        elif key in ['customizationIdentifier', 'uniqueId', 'tsePublicKey', 'tseSerialNumber']:
            return self.__get_string(key)
        elif key in ['tseDescription', 'formFactor',]:
            return self.__get_chars(key)
        elif key in ['softwareVersion', 'hardwareVersion']:
            return self.__get_version(key)
        elif key in ['certificateExpirationDate',]:
            return self.__get_date(key)
        else:
            raise AttributeError('unimplemented: %s' % key)


    def __get_info_uint64(self, key):
        getattr(self.wormlib, 'worm_info_'+key).restype = c_uint64
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo,)
        ret = getattr(self.wormlib, 'worm_info_'+key)(self.info)
        return ret

        
    def __get_chars(self, key):
        getattr(self.wormlib, 'worm_info_'+key).restype = c_char_p
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo,)
        ret = getattr(self.wormlib, 'worm_info_'+key)(self.info)
        return ret.decode('latin1')

    
    def __get_string(self, key):
        s = c_char_p()
        sLength = c_uint64()
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo, POINTER(c_char_p), POINTER(c_uint64))
        getattr(self.wormlib, 'worm_info_'+key)(self.info, byref(s), byref(sLength))
        s = cast(s, POINTER(c_char))
        ret = string_at(s, size=sLength.value)
        return ret
        
    def __get_version(self, key):
        getattr(self.wormlib, 'worm_info_'+key).restype = c_uint64
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo,)
        ret = getattr(self.wormlib, 'worm_info_'+key)(self.info)
        major = (ret & 0xffff0000) >> 16 
        minor = (ret & 0x0000ff00) >> 8 
        patch = (ret & 0x000000ff) 
        return (major, minor, patch)


    def __get_date(self, key):
        getattr(self.wormlib, 'worm_info_'+key).restype = c_uint64
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo,)
        ret = getattr(self.wormlib, 'worm_info_'+key)(self.info)
        return datetime.datetime.fromtimestamp(ret)


