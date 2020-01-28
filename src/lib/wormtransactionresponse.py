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
        sLength = c_uint64()
        getattr(self.wormlib, 'worm_transaction_response_'+key).argtypes = (WormTransactionResponse, POINTER(c_char_p), POINTER(c_uint64))
        getattr(self.wormlib, 'worm_transaction_response_'+key)(self.response, byref(s), byref(sLength))
        s = cast(s, POINTER(c_char))
        ret = string_at(s, size=sLength.value)
        return ret
        

    def __get_date(self, key):
        getattr(self.wormlib, 'worm_transaction_response_'+key).restype = c_uint64
        getattr(self.wormlib, 'worm_transaction_response_'+key).argtypes = (WormTransactionResponse,)
        ret = getattr(self.wormlib, 'worm_transaction_response_'+key)(self.response)
        return datetime.datetime.fromtimestamp(ret)


