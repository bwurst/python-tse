import os.path
import datetime
from ctypes import *
from wormtypes import *
from worminfo import Worm_Info
from wormentry import Worm_Entry
from wormtransactionresponse import Worm_Transaction_Response
from wormexception import WormException, WormError_to_exception

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
        self.info = None
        self.entry = None
        if not mountpoint:
            mountpoint = find_mountpoint()
        if not mountpoint:
            raise WormException(WORM_ERROR_NO_WORM_CARD, 'Cannot find TSE unit!')
        if not library:
            library = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../so/libWormAPI.so'))
        if not os.path.exists(library):
            raise WormException(WORM_ERROR_UNKNOWN, 'Cannot find TSE / SMAERS library. Was expected as %s' % library)
        self.wormlib = cdll.LoadLibrary(library)

        self.ctx = WormContext()
        self.info = None

        self.wormlib.worm_init.restype = WormError
        self.wormlib.worm_init.argtypes = (POINTER(WormContext), c_char_p)
        ret = self.wormlib.worm_init(byref(self.ctx), mountpoint.encode('utf-8'))
        WormError_to_exception(ret)
        
        self.entry = Worm_Entry(self)
        self.info = Worm_Info(self)
        if self.info.initializationState == WORM_INIT_DECOMMISSIONED:
            raise WormException(WORM_ERROR_TSE_DECOMMISSIONED, 'TSE ist unwiderruflich außer Betrieb gesetzt und kann nicht mehr benutzt werden!')
        elif self.info.initializationState == WORM_INIT_UNINITIALIZED:
            import warnings
            warnings.warn(Warning('TSE ist noch nicht initialisiert. Bitte zuerst initialisieren!'))
        


    def __del__(self):
        if self.info:
            del(self.info)
        if self.wormlib:
            self.wormlib.worm_cleanup.restype = WormError
            ret = self.wormlib.worm_cleanup(self.ctx)
            WormError_to_exception(ret)

    ####################################################################
    # Library Information
    ####################################################################

    def getVersion(self):
        self.wormlib.worm_getVersion.restype = c_char_p
        ret = self.wormlib.worm_getVersion()
        # liefert bytes. Wir konvertieren als latin1, da es da keine UnicodeDecodeErrors geben kann.
        return ret.decode('latin1')

    def logTimeFormat(self):
        self.wormlib.worm_logTimeFormat.restype = c_char_p
        ret = self.wormlib.worm_logTimeFormat()
        return ret.decode('latin1')


    def signatureAlgorithm(self):
        self.wormlib.worm_signatureAlgorithm.restype = c_char_p
        ret = self.wormlib.worm_signatureAlgorithm()
        return ret.decode('latin1')

    ####################################################################
    # TSE-Configuration
    ####################################################################
    
    def tse_factoryReset(self):
        self.wormlib.worm_tse_factoryReset.restype = WormError
        self.wormlib.worm_tse_factoryReset.argtypes = (WormContext, )
        ret = self.wormlib.worm_tse_factoryReset(self.ctx)
        WormError_to_exception(ret)
        self.info.update()
        return ret
    
    def tse_prepare(self, adminpuk, adminpin, time_admin_pin = None):
        '''Kann beim Programmstart aufgerufen werden und kümmert sich um 
        tse_setup() bei Bedarf oder richtet die clientid ein'''
        if not time_admin_pin:
            time_admin_pin = self.time_admin_pin
        if self.info.initializationState == WORM_INIT_UNINITIALIZED:
            self.tse_setup(adminpuk, adminpin, time_admin_pin)
            self.tse_updateTime()
        if not self.info.hasPassedSelfTest:
            try:
                self.tse_runSelfTest()
            except WormException as e:
                if e.errno == WORM_ERROR_CLIENT_NOT_REGISTERED:
                    self.user_login(WORM_USER_ADMIN, adminpin)
                    self.tse_registerClient(adminpin = adminpin)
                    self.user_logout(WORM_USER_ADMIN)
                # self-test nochmal ausführen. Schlägt dieser nochmal fehl, wird die exception durchgereicht.
                self.tse_runSelfTest()
        if not self.info.hasValidTime:
            self.tse_updateTime()
    
    
    def tse_setup(self, adminpuk, adminpin, timeadminpin):
        if self.info.initializationState == WORM_INIT_INITIALIZED:
            raise WormException(WORM_ERROR_UNKNOWN, 'initialization ist schon erfolgt!')
        # Es muss mindestens ein SelfTest gemacht werden vor dem setup.
        try:
            self.tse_runSelfTest()
        except WormException:
            # Dieser Self-Test schlägt fehl, das ist by design.
            pass
        credentialseed = b'SwissbitSwissbit'
        if type(adminpuk) == str:
            adminpuk = adminpuk.encode('latin1')
        if len(adminpuk) != 6:
            raise ValueError('Admin-PUK muss genau 6 Stellen lang sein')
        if type(adminpin) == str:
            adminpin = adminpin.encode('latin1')
        if len(adminpin) != 5:
            raise ValueError('Admin-PIN muss genau 5 Stellen lang sein')
        if type(timeadminpin) == str:
            timeadminpin = timeadminpin.encode('latin1')
        if len(timeadminpin) != 5:
            raise ValueError('Time-Admin-PIN muss genau 5 Stellen lang sein')
        self.wormlib.worm_tse_setup.restype = WormError
        self.wormlib.worm_tse_setup.argtypes = (WormContext, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p)
        ret = self.wormlib.worm_tse_setup(self.ctx, credentialseed, len(credentialseed), 
                                          adminpuk, len(adminpuk), adminpin, len(adminpin), timeadminpin, len(timeadminpin), 
                                          self.clientid.encode('latin1'))
        WormError_to_exception(ret)
        self.info.update()
        return ret
    
    
    def tse_runSelfTest(self):
        self.wormlib.worm_tse_runSelfTest.argtypes = (WormContext, c_char_p)
        self.wormlib.worm_tse_runSelfTest.restype = WormError
        ret = self.wormlib.worm_tse_runSelfTest(self.ctx, self.clientid.encode('latin1'))
        WormError_to_exception(ret)
        self.info.update()
        return ret
        
    def tse_updateTime(self):
        if self.time_admin_pin:
            self.user_login(WORM_USER_TIME_ADMIN, self.time_admin_pin)
        self.wormlib.worm_tse_updateTime.argtypes = (WormContext, c_uint64)
        self.wormlib.worm_tse_updateTime.restype = WormError
        ret = self.wormlib.worm_tse_updateTime(self.ctx, int(datetime.datetime.now().timestamp()))
        WormError_to_exception(ret)
        self.info.update()
        return ret
        
    def tse_listRegisteredClients(self):
        skip = 0
        clients = []
        while True:
            _clients = WormRegisteredClients()
            self.wormlib.worm_tse_listRegisteredClients.argtypes = (WormContext, c_int, POINTER(WormRegisteredClients))
            ret = self.wormlib.worm_tse_listRegisteredClients(self.ctx, skip, _clients)
            WormError_to_exception(ret)
            data = False
            for entry in _clients.clientIds:
                id = cast(entry, c_char_p).value.decode('latin1')
                if id:
                    clients.append(id)
                    data = True
            if len(clients) >= _clients.amount or not data:
                break
            skip += 16
        return clients 
    
    def tse_registerClient(self, clientid = None, adminpin = None):
        if not clientid:
            clientid = self.clientid
        if adminpin:
            self.user_login(WORM_USER_ADMIN, adminpin)
        self.wormlib.worm_tse_registerClient.argtypes = (WormContext, c_char_p)
        ret = self.wormlib.worm_tse_registerClient(self.ctx, clientid.encode('latin1'))
        WormError_to_exception(ret)
        
    def tse_deregisterClient(self, clientid = None):
        if not clientid:
            clientid = self.clientid
        self.wormlib.worm_tse_deregisterClient.argtypes = (WormContext, c_char_p)
        ret = self.wormlib.worm_tse_deregisterClient(self.ctx, clientid.encode('latin1'))
        WormError_to_exception(ret)
        
    def user_login(self, userid, pin):
        pin = pin.encode('latin1')
        remainingRetries = c_int()
        
        self.wormlib.worm_user_login.argtypes = (WormContext, c_int, c_char_p, c_int, POINTER(c_int))
        self.wormlib.worm_user_login.restype = WormError
        ret = self.wormlib.worm_user_login(self.ctx, userid, pin, len(pin), byref(remainingRetries))
        WormError_to_exception(ret)
        self.info.update()
        return remainingRetries.value
        
    def user_logout(self, userid):
        self.wormlib.worm_user_logout.argtypes = (WormContext, c_int)
        self.wormlib.worm_user_logout.restype = WormError
        ret = self.wormlib.worm_user_logout(self.ctx, userid)
        WormError_to_exception(ret)
        self.info.update()
        
    def user_deriveInitialCredentials(self):
        seed = b'SwissbitSwissbit'
        adminpuk = c_char_p(b'xxxxxx')
        adminpin = c_char_p(b'xxxxx')
        timeadminpin = c_char_p(b'xxxxx')
        self.wormlib.worm_user_deriveInitialCredentials.argtypes = (WormContext, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int)
        self.wormlib.worm_user_deriveInitialCredentials.restype = WormError
        ret = self.wormlib.worm_user_deriveInitialCredentials(self.ctx, seed, len(seed), adminpuk, 6, adminpin, 5, timeadminpin, 5)
        WormError_to_exception(ret)
        print('adminPUK:', adminpuk.value.decode('latin1'))
        print('adminPIN:', adminpin.value.decode('latin1'))
        print('timeadminPIN:', timeadminpin.value.decode('latin1'))
        return (adminpuk.value.decode('latin1'), adminpin.value.decode('latin1'), timeadminpin.value.decode('latin1'))
        
        
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
            raise WormException(WORM_ERROR_WRONG_STATE_NEEDS_ACTIVE_CTSS, 'TSE not ready!')

        
    def transaction_start(self, processdata, processtype):
        self.__pre_transaction_checks()
        if type(processdata) == str:
            processdata = processdata.encode('utf-8')
        if type(processtype) == str:
            processtype = processtype.encode('utf-8')
        assert type(processdata) == bytes, 'processdata ist kein byte-string'
        assert type(processtype) == bytes, 'processtype ist kein byte-string'
        r = Worm_Transaction_Response(self)
        self.wormlib.worm_transaction_start.argtypes = (WormContext, c_char_p, c_char_p, c_int, c_char_p, WormTransactionResponse)
        self.wormlib.worm_transaction_start.restype = WormError
        ret = self.wormlib.worm_transaction_start(self.ctx, self.clientid.encode('latin1'), processdata, 
                                                  len(processdata), processtype, r.response)
        WormError_to_exception(ret)
        return r

        
    def transaction_update(self, transactionnumber, processdata, processtype):
        self.__pre_transaction_checks()
        if type(processdata) == str:
            processdata = processdata.encode('utf-8')
        if type(processtype) == str:
            processtype = processtype.encode('utf-8')
        assert type(processdata) == bytes, 'processdata ist kein byte-string'
        assert type(processtype) == bytes, 'processtype ist kein byte-string'
        r = Worm_Transaction_Response(self)
        self.wormlib.worm_transaction_update.argtypes = (WormContext, c_char_p, c_uint64, c_char_p, c_int, c_char_p, WormTransactionResponse)
        self.wormlib.worm_transaction_update.restype = WormError
        ret = self.wormlib.worm_transaction_update(self.ctx, self.clientid.encode('latin1'), transactionnumber, processdata, 
                                                  len(processdata), processtype, r.response)
        WormError_to_exception(ret)
        return r
        
    def transaction_finish(self, transactionnumber, processdata, processtype):
        self.__pre_transaction_checks()
        if type(processdata) == str:
            processdata = processdata.encode('utf-8')
        if type(processtype) == str:
            processtype = processtype.encode('utf-8')
        assert type(processdata) == bytes, 'processdata ist kein byte-string'
        assert type(processtype) == bytes, 'processtype ist kein byte-string'
        r = Worm_Transaction_Response(self)
        self.wormlib.worm_transaction_finish.argtypes = (WormContext, c_char_p, c_uint64, c_char_p, c_int, c_char_p, WormTransactionResponse)
        self.wormlib.worm_transaction_finish.restype = WormError
        ret = self.wormlib.worm_transaction_finish(self.ctx, self.clientid.encode('latin1'), transactionnumber, processdata, 
                                                  len(processdata), processtype, r.response)
        WormError_to_exception(ret)
        self.info.update()
        return r
        
    def transaction_listStartedTransactions(self, skip=0):
        self.__pre_transaction_checks()
        numbers_buffer = (c_uint64 * 62)()
        count = c_int()
        self.wormlib.worm_transaction_listStartedTransactions.argtypes = (WormContext, c_char_p, c_uint64, c_uint64 * 62, c_int, POINTER(c_int))
        self.wormlib.worm_transaction_listStartedTransactions.restype = WormError
        ret = self.wormlib.worm_transaction_listStartedTransactions(self.ctx, self.clientid.encode('latin1'), skip, numbers_buffer, 62, byref(count))
        WormError_to_exception(ret)
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
        WormError_to_exception(res)
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
                ret = self.wormlib.worm_export_tar_filtered_time(self.ctx, c_uint64(time_start), c_uint64(time_end), c_char_p(clientid), callback, None)
                WormError_to_exception(ret)
            elif trxid_start:
                assert type(trxid_start) == int
                assert type(trxid_end) == int
                ret = self.wormlib.worm_export_tar_filtered_transaction(self.ctx, c_uint64(trxid_start), c_uint64(trxid_end), c_char_p(clientid), callback, None)
                WormError_to_exception(ret)
            else:
                ret = self.wormlib.worm_export_tar(self.ctx, callback, None)
                WormError_to_exception(ret)
    
    
    def export_tar_incremental(self, filename, lastState=None):
        '''inkrementeller export
        returns (firstSignatureCounter, lastSignatureCounter, newState)
        newState muss beim nächsten inkrementellen export als lastState übergeben werden.'''
        CALLBACK = CFUNCTYPE(c_int, POINTER(c_char), c_uint64, c_void_p)
        callback = CALLBACK(self.export_tar_callback)
        with open(filename, 'wb') as self.tarfile:
            firstSignatureCounter = c_uint64()
            lastSignatureCounter = c_uint64()
            last_state = None
            last_state_len = 0
            if lastState:
                last_state = c_char_p(lastState)
                last_state_len = c_int(len(lastState))
            new_state = cast(create_string_buffer(WORM_EXPORT_TAR_INCREMENTAL_STATE_SIZE), c_char_p)
            new_state_len = c_int(WORM_EXPORT_TAR_INCREMENTAL_STATE_SIZE)
            ret = self.wormlib.worm_export_tar_incremental(self.ctx, last_state, last_state_len, new_state, new_state_len, byref(firstSignatureCounter), byref(lastSignatureCounter), callback, None)
            WormError_to_exception(ret)
            new_state = cast(new_state, POINTER(c_char))
            return_state = string_at(new_state, new_state_len)
            return (firstSignatureCounter.value, lastSignatureCounter.value, return_state)
    
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

