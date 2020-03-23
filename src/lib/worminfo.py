# TSE Connection Library
# Copyright (C) 2020 Bernd Wurst <bernd@mosterei-wurst.de>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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
        #WormError_to_exception(ret)
        #Wenn wir hier eine Exception ausgeben, bricht das an manchen Stellen, falls die TSE nicht angesteckt ist...


    def __del__(self):
        if self.info:
            self.wormlib.worm_info_free(self.info)
            self.info = None

    def __getattr__(self, key):
        if key in ['isDevelopmentFirmware', 'isStoreOpen', 'hasValidTime', 'hasPassedSelfTest', 
                   'isCtssInterfaceActive', 'isErsInterfaceActive', 'isExportEnabledIfCspTestFails',
                   'isDataImportInProgress', 'isTransactionInProgress', 'hasChangedPuk', 'hasChangedAdminPin',
                   'hasChangedTimeAdminPin']:
            return bool(self.__get_info_uint32(key))
        elif key in ['tarExportSizeInSectors', 'tarExportSize']:
            return self.__get_info_uint64(key)
        elif key in ['size', 'capacity', 'timeUntilNextSelfTest', 'startedTransactions', 'maxStartedTransactions',
                     'createdSignatures', 'maxSignatures', 'remainingSignatures', 'maxTimeSynchronizationDelay',
                     'maxUpdateDelay', 'registeredClients', 'maxRegisteredClients', 'initializationState']:
            return self.__get_info_uint32(key)
        elif key in ['customizationIdentifier', 'uniqueId']:
            return self.__get_string(key)
        elif key in ['tsePublicKey', 'tseSerialNumber']:
            return self.__get_string64(key)
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

        
    def __get_info_uint32(self, key):
        getattr(self.wormlib, 'worm_info_'+key).restype = c_uint32
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
        sLength = c_uint()
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo, POINTER(c_char_p), POINTER(c_uint))
        getattr(self.wormlib, 'worm_info_'+key)(self.info, byref(s), byref(sLength))
        s = cast(s, POINTER(c_char))
        ret = string_at(s, size=sLength.value)
        return ret


    def __get_string64(self, key):
        s = c_char_p()
        sLength = c_uint64()
        getattr(self.wormlib, 'worm_info_'+key).argtypes = (WormInfo, POINTER(c_char_p), POINTER(c_uint64))
        getattr(self.wormlib, 'worm_info_'+key)(self.info, byref(s), byref(sLength))
        s = cast(s, POINTER(c_char))
        ret = string_at(s, size=sLength.value)
        return ret
        
    def __get_version(self, key):
        getattr(self.wormlib, 'worm_info_'+key).restype = c_uint32
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


