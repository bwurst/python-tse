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


class Worm_Transaction_Response:
    def __init__(self, worm):
        self.ctx = worm.ctx
        self.wormlib = worm.wormlib

        self.wormlib.worm_transaction_response_new.argtypes = (WormContext,)
        self.wormlib.worm_transaction_response_new.restype = WormTransactionResponse
        self.response = cast(self.wormlib.worm_transaction_response_new(self.ctx), WormTransactionResponse)

    def __del__(self):
        if self.response:
            self.wormlib.worm_transaction_response_free(self.response)
            self.response = None

    def __getattr__(self, key):
        if key in ['signatureCounter', 'transactionNumber']:
            return self.__get_info_uint64(key)
        elif key in ['serialNumber', 'signature',]:
            return self.__get_string(key)
        elif key in ['logTime',]:
            return self.__get_date(key)
        else:
            raise AttributeError('unimplemented: %s' % key)


    def __get_info_uint64(self, key):
        getattr(self.wormlib, 'worm_transaction_response_'+key).restype = c_uint64
        getattr(self.wormlib, 'worm_transaction_response_'+key).argtypes = (WormTransactionResponse,)
        ret = getattr(self.wormlib, 'worm_transaction_response_'+key)(self.response)
        return ret

        
    def __get_string(self, key):
        s = c_char_p()
        sLength = worm_uint()
        getattr(self.wormlib, 'worm_transaction_response_'+key).argtypes = (WormTransactionResponse, POINTER(c_char_p), POINTER(worm_uint))
        getattr(self.wormlib, 'worm_transaction_response_'+key)(self.response, byref(s), byref(sLength))
        s = cast(s, POINTER(c_char))
        ret = string_at(s, size=sLength.value)
        return ret
        

    def __get_date(self, key):
        getattr(self.wormlib, 'worm_transaction_response_'+key).restype = worm_uint
        getattr(self.wormlib, 'worm_transaction_response_'+key).argtypes = (WormTransactionResponse,)
        ret = getattr(self.wormlib, 'worm_transaction_response_'+key)(self.response)
        return datetime.datetime.fromtimestamp(ret)


