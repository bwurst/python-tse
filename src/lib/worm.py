import os.path
from ctypes import *
from wormtypes import *
import datetime
from worminfo import Worm_Info
from wormentry import Worm_Entry
from wormtransactionresponse import Worm_Transaction_Response

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

    def __init__(self, clientid, mountpoint = None, time_admin_pin = None, library = None):
        self.time_admin_pin = time_admin_pin
        self.clientid = clientid
        if not mountpoint:
            mountpoint = find_mountpoint()
        if not mountpoint:
            raise RuntimeError('Cannot find TSE unit!')
        if not library:
            library = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))
        if not os.path.exists(library):
            raise RuntimeError('Cannot find TSE / SMAERS library. Was expected as %s' % library)
        self.wormlib = cdll.LoadLibrary(library)

        self.ctx = WormContext()
        self.info = None

        self.wormlib.worm_init.restype = WormError
        self.wormlib.worm_init.argtypes = (POINTER(WormContext), c_char_p)
        ret = self.wormlib.worm_init(byref(self.ctx), mountpoint.encode('utf-8'))

        # FIXME: returncode auswerten
        if ret != 0:
            print('return code for worm_init() => ', ret)
        
        self.entry = Worm_Entry(self)
        self.info = Worm_Info(self)
        if self.info.initializationState == WORM_INIT_DECOMMISSIONED:
            raise RuntimeError('TSE ist unwiderruflich außer Betrieb gesetzt und kann nicht mehr benutzt werden!')
        elif self.info.initializationState == WORM_INIT_UNINITIALIZED:
            import warnings
            warnings.warn(RuntimeWarning('TSE ist noch nicht initialisiert. Bitte zuerst initialisieren!'))
        


    def __del__(self):
        if self.info:
            del(self.info)
        self.wormlib.worm_cleanup.restype = WormError
        ret = self.wormlib.worm_cleanup(self.ctx)
        # FIXME: returncode auswerten
        if ret != 0:
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
        self.info.update()
        return ret
    
    def tse_setup(self, credentialseed, adminpuk, adminpin, timeadminpin):
        if self.info.initializationState == WORM_INIT_INITIALIZED:
            print('initialization ist schon erfolgt!')
            return False
        self.wormlib.worm_tse_setup.restype = WormError
        self.wormlib.worm_tse_setup.argtypes = (WormContext, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p)
        ret = self.wormlib.worm_tse_setup(self.ctx, credentialseed.encode('ascii'), len(credentialseed), 
                                          adminpuk.encode('ascii'), len(adminpuk), adminpin.encode('ascii'), 
                                          len(adminpin), timeadminpin.encode('ascii'), len(timeadminpin), 
                                          self.clientid.encode('ascii'))
        # FIXME: Error handling
        self.info.update()
        return ret
    
    
    def tse_runSelfTest(self):
        self.wormlib.worm_tse_runSelfTest.argtypes = (WormContext, c_char_p)
        self.wormlib.worm_tse_runSelfTest.restype = WormError
        ret = self.wormlib.worm_tse_runSelfTest(self.ctx, self.clientid.encode('ascii'))
        self.info.update()
        return ret
        
    def tse_updateTime(self):
        if self.time_admin_pin:
            self.user_login(WORM_USER_TIME_ADMIN, self.time_admin_pin)
        self.wormlib.worm_tse_updateTime.argtypes = (WormContext, c_uint64)
        self.wormlib.worm_tse_updateTime.restype = WormError
        ret = self.wormlib.worm_tse_updateTime(self.ctx, int(datetime.datetime.now().timestamp()))
        self.info.update()
        return ret
        
    
        
    def user_login(self, userid, pin):
        WormUserId = userid # WORM_USER_ADMIN
        pin = pin.encode('ascii')
        remainingRetries = c_int()
        
        self.wormlib.worm_user_login.argtypes = (WormContext, c_int, c_char_p, c_int, POINTER(c_int))
        self.wormlib.worm_user_login.restype = WormError
        ret = self.wormlib.worm_user_login(self.ctx, WormUserId, pin, len(pin), byref(remainingRetries))

        print('remainingRetries: ', remainingRetries.value)
        print(ret)
        self.info.update()
        return ret
        
    def user_deriveInitialCredentials(self):
        seed = b'SwissbitSwissbit'
        adminpuk = c_char_p(b'xxxxxx')
        adminpin = c_char_p(b'xxxxx')
        timeadminpin = c_char_p(b'xxxxx')
        
        self.wormlib.worm_user_deriveInitialCredentials.argtypes = (WormContext, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int)
        self.wormlib.worm_user_deriveInitialCredentials.restype = WormError
        ret = self.wormlib.worm_user_deriveInitialCredentials(self.ctx, seed, len(seed), adminpuk, 6, adminpin, 5, timeadminpin, 5)
        if ret != 0:
            print(ret)
        print('adminPUK:', adminpuk.value.decode('ascii'))
        print('adminPIN:', adminpin.value.decode('ascii'))
        print('timeadminPIN:', timeadminpin.value.decode('ascii'))
        return (adminpuk.value.decode('ascii'), adminpin.value.decode('ascii'), timeadminpin.value.decode('ascii'))
        
        
    ####################################################################
    # Transactions
    ####################################################################
        
    def __pre_transaction_checks(self):
        self.info.update()
        if not self.info.hasPassedSelfTest:
            self.tse_runSelfTest()
        if not self.info.hasValidTime:
            self.tse_updateTime()
        if not self.info.isCtssInterfaceActive:
            raise RuntimeError('TSE not ready!')

        
    def transaction_start(self, processdata, processtype):
        self.__pre_transaction_checks()
        r = Worm_Transaction_Response(self)
        self.wormlib.worm_transaction_start.argtypes = (WormContext, c_char_p, c_char_p, c_int, c_char_p, WormTransactionResponse)
        self.wormlib.worm_transaction_start.restype = WormError
        ret = self.wormlib.worm_transaction_start(self.ctx, self.clientid.encode('ascii'), processdata, 
                                                  len(processdata), processtype.encode('ascii'), r.response)
        if ret != 0:
            print('transaction_start() =>', ret)
        #print(self.wormlib.worm_transaction_response_transactionNumber(byref(r.response)))
        # FIXME: return code / error handling
        return r

        
    def transaction_update(self, transactionnumber, processdata, processtype):
        self.__pre_transaction_checks()
        r = Worm_Transaction_Response(self)
        self.wormlib.worm_transaction_update.argtypes = (WormContext, c_char_p, c_uint64, c_char_p, c_int, c_char_p, WormTransactionResponse)
        self.wormlib.worm_transaction_update.restype = WormError
        ret = self.wormlib.worm_transaction_update(self.ctx, self.clientid.encode('ascii'), transactionnumber, processdata, 
                                                  len(processdata), processtype.encode('ascii'), r.response)
        if ret != 0:
            print('transaction_update() =>', ret)
        #print(self.wormlib.worm_transaction_response_transactionNumber(byref(r.response)))
        # FIXME: return code / error handling
        return r
        
    def transaction_finish(self, transactionnumber, processdata, processtype):
        self.__pre_transaction_checks()
        r = Worm_Transaction_Response(self)
        self.wormlib.worm_transaction_finish.argtypes = (WormContext, c_char_p, c_uint64, c_char_p, c_int, c_char_p, WormTransactionResponse)
        self.wormlib.worm_transaction_finish.restype = WormError
        ret = self.wormlib.worm_transaction_finish(self.ctx, self.clientid.encode('ascii'), transactionnumber, processdata, 
                                                  len(processdata), processtype.encode('ascii'), r.response)
        if ret != 0:
            print('transaction_finish() =>', ret)
        #print(self.wormlib.worm_transaction_response_transactionNumber(byref(r.response)))
        # FIXME: return code / error handling
        self.info.update()
        return r
        
    def transaction_listStartedTransactions(self, skip=0):
        numbers_buffer = (c_uint64 * 62)()
        count = c_int()
        self.wormlib.worm_transaction_listStartedTransactions.argtypes = (WormContext, c_char_p, c_uint64, c_uint64 * 62, c_int, POINTER(c_int))
        self.wormlib.worm_transaction_listStartedTransactions.restype = WormError
        ret = self.wormlib.worm_transaction_listStartedTransactions(self.ctx, self.clientid.encode('ascii'), skip, numbers_buffer, 62, byref(count))
        if ret != 0:
            print('transaction_listStartedTransactions() =>', ret)
        return numbers_buffer[:count.value]
            
        
    ####################################################################
    # Export
    ####################################################################
    
    def getLogMessageCertificate(self):
        s = c_char_p()
        buffer = pointer((c_char * 1024*1024)())
        sLength = c_uint64(1024*1024) # 1 MB
        self.wormlib.worm_getLogMessageCertificate.argtypes = (WormContext, POINTER(c_char * 1024*1024), POINTER(c_uint64))
        res = self.wormlib.worm_getLogMessageCertificate(self.ctx, buffer, byref(sLength))
        if res != 0:
            print('getLogMessageCertificate() =>', res)
        s = cast(buffer, POINTER(c_char))
        ret = string_at(s, size=sLength.value)
        return ret

    def export_tar(self, filename, clientid=None, time_start=None, time_end=None, trxid_start=None, trxid_end=None):
        CALLBACK = CFUNCTYPE(c_int, POINTER(c_char), c_uint64, c_void_p)
        callback = CALLBACK(self.export_tar_callback)
        with open(filename, 'wb') as self.tarfile:
            if time_start:
                if type(time_start) == datetime.datetime:
                    time_start = int(time_start.timestamp())
                    time_end = int(time_start.timestamp())
                assert type(time_start) == int
                assert type(time_end) == int
                self.wormlib.worm_export_tar_filtered_time(self.ctx, c_uint64(time_start), c_uint64(time_end), c_char_p(clientid), callback, None)
            elif trxid_start:
                assert type(trxid_start) == int
                assert type(trxid_end) == int
                self.wormlib.worm_export_tar_filtered_transaction(self.ctx, c_uint64(trxid_start), c_uint64(trxid_end), c_char_p(clientid), callback, None)
            else:
                self.wormlib.worm_export_tar(self.ctx, callback, None)
    
    
    def export_tar_callback(self, chunk, chunklen, data):
        chunk = cast(chunk, POINTER(c_char))
        if not self.tarfile:
            # Sollte schon vorhanden sein, sonst Fehler
            return 1
        self.tarfile.write(string_at(chunk, chunklen))
        return 0



        
    ####################################################################
    # disfunctional
    ####################################################################
        
        
    def user_unblock(self):
        WormUserId = WORM_USER_TIME_ADMIN
        puk = c_wchar_p(config.PUK)
        pukLength = 6 
        newPin = c_wchar_p(config.PIN_TIME_ADMIN)
        newPinLength = 5
        remainingRetries = c_int()
        
        self.wormlib.worm_user_unblock.argtypes = (WormContext, c_int, c_wchar_p, c_int, c_wchar_p, c_int, POINTER(c_int))
        self.wormlib.worm_user_unblock.restype = WormError
        ret = self.wormlib.worm_user_unblock(self.ctx, WormUserId, puk, pukLength, newPin, newPinLength, remainingRetries)

        print('remainingRetries: ', remainingRetries.value)
        print(ret)
        return ret
        
        
    # FIXME: Diese Funktion gibt nichts zurück
    def flash_health_summary(self):
        uncorrectableEccErrors = c_uint32()
        percentageRemainingSpareBlocks = c_uint8()
        percentageRemainingEraseCounts = c_uint8()
        percentageRemainingTenYearsDataRetention = c_uint8()

        self.wormlib.worm_flash_health_summary.argtypes = (WormContext, POINTER(c_uint32), POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint8))
        self.wormlib.worm_flash_health_summary.restype = WormError
        ret = self.wormlib.worm_flash_health_summary(self.ctx, byref(uncorrectableEccErrors), byref(percentageRemainingSpareBlocks),
                                                      byref(percentageRemainingEraseCounts), byref(percentageRemainingTenYearsDataRetention))

        print(ret)
        print(uncorrectableEccErrors.value)
        print(percentageRemainingSpareBlocks.value)
        print(percentageRemainingEraseCounts.value)
        print(percentageRemainingTenYearsDataRetention.value)

