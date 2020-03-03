import datetime
from ctypes import *
from wormtypes import *


class Worm_Entry:
    def __init__(self, worm):
        self.ctx = worm.ctx
        self.wormlib = worm.wormlib

        self.wormlib.worm_entry_new.argtypes = (WormContext,)
        self.wormlib.worm_entry_new.restype = WormEntry
        self.entry = cast(self.wormlib.worm_entry_new(self.ctx), WormEntry)


    def __del__(self):
        if self.entry:
            self.wormlib.worm_entry_free(self.entry)
            self.entry = None

    def __getattr__(self, key):
        if key in ['isValid',]:
            return bool(self.__get_info_uint(key))
        elif key in ['id', ]:
            return self.__get_info_uint32(key)
        elif key in ['logMessageLength', 'processDataLength', 'type']:
            return self.__get_info_uint64(key)
        else:
            raise AttributeError('unimplemented: %s' % key)


    def __get_info_uint(self, key):
        getattr(self.wormlib, 'worm_entry_'+key).restype = c_uint
        getattr(self.wormlib, 'worm_entry_'+key).argtypes = (WormEntry,)
        ret = getattr(self.wormlib, 'worm_entry_'+key)(self.entry)
        return ret


    def __get_info_uint32(self, key):
        getattr(self.wormlib, 'worm_entry_'+key).restype = c_uint32
        getattr(self.wormlib, 'worm_entry_'+key).argtypes = (WormEntry,)
        ret = getattr(self.wormlib, 'worm_entry_'+key)(self.entry)
        return ret


    def __get_info_uint64(self, key):
        getattr(self.wormlib, 'worm_entry_'+key).restype = c_uint64
        getattr(self.wormlib, 'worm_entry_'+key).argtypes = (WormEntry,)
        ret = getattr(self.wormlib, 'worm_entry_'+key)(self.entry)
        return ret


    def iterate_first(self):
        ret = self.wormlib.worm_entry_iterate_first(self.entry)
        return ret
    
    def iterate_last(self):
        ret = self.wormlib.worm_entry_iterate_last(self.entry)
        return ret
    
    def iterate_id(self, id):
        self.wormlib.worm_entry_iterate_id.argtypes(WormEntry, c_uint32)
        ret = self.wormlib.worm_entry_iterate_id(self.entry, id)
        return ret
    
    def iterate_next(self):
        ret = self.wormlib.worm_entry_iterate_next(self.entry)
        return ret
        
    def readLogMessage(self):
        # FIXME So ist das nicht gedacht aber wir rechnen nicht mit sehr großen Datenmengen
        length = self.logMessageLength
        buffer = pointer((c_char * length)())
        self.wormlib.worm_entry_readLogMessage.restype = WormError
        self.wormlib.worm_entry_readLogMessage.argtypes = (WormEntry, POINTER(c_char*length), worm_uint)
        ret = self.wormlib.worm_entry_readLogMessage(self.entry, buffer, length)
        s = cast(buffer, POINTER(c_char))
        return string_at(s, size=length)

    def readProcessData(self, offset=0):
        # FIXME So ist das nicht gedacht aber wir rechnen nicht mit sehr großen Datenmengen
        length = self.processDataLength - offset
        buffer = pointer((c_char * length)())
        self.wormlib.worm_entry_readProcessData.restype = WormError
        self.wormlib.worm_entry_readProcessData.argtypes = (WormEntry, worm_uint, POINTER(c_char*length), worm_uint)
        ret = self.wormlib.worm_entry_readProcessData(self.entry, offset, buffer, length)
        s = cast(buffer, POINTER(c_char))
        return string_at(s, size=length)

