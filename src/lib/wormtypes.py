from ctypes import *

# Das ist nur der Pointer auf ein struct
WormContext = c_void_p

WormError = c_int


class WormInitializationState():
    (WORM_INIT_UNINITIALIZED,
    WORM_INIT_INITIALIZED,
    WORM_INIT_DECOMMISSIONED) = map(c_int, range(3))




class WormInfo(Structure):
    
    wormInitializationState = WormInitializationState() # FIXME: das funktionert so noch nicht

    _fields_ = [
                ("isDevelopmentFirmware", c_bool),
                ("hasValidTime", c_bool),
                ("hasPassedSelfTest", c_bool),
                ("isCtssInterfaceActive", c_bool),
                ("isExportEnabledIfCspTestFails", c_bool),
                ("isDataImportInProgress", c_bool),
                ("hasChangedPuk", c_bool),
                ("hasChangedAdminPin", c_bool),
                ("hasChangedTimeAdminPin", c_bool),

                ("maxRegisteredClients", c_uint32),
                ("registeredClients", c_uint32),
                ("startedTransactions", c_uint32),
                ("maxStartedTransactions", c_uint32),
                ("createdSignatures", c_uint32),
                ("maxSignatures", c_uint32),
                ("remainingSignatures", c_uint32),
                ("maxTimeSynchronizationDelay", c_uint32),
                ("maxUpdateDelay", c_uint32),
                ("certificateExpirationDate", c_uint64),
                ("tarExportSizeInSectors", c_uint64),
                ("tarExportSize", c_uint64),
                ("hardwareVersion", c_uint32),
                ("softwareVersion", c_uint32),
                ("size", c_int32),
                ("capacity", c_uint32),
                ("timeUntilNextSelfTest", c_uint32),
                
                ("tsePublicKey", c_ubyte), # original: std::vector< unsigned char >
                ("tseSerialNumber", c_ubyte), # original: std::vector< unsigned char >
                ("customizationIdentifier", c_ubyte), # original: std::vector< unsigned char >
                
                ("tseDescription", c_wchar_p),  # original: std::string
                ("formFactor", c_wchar_p),  # original: std::string
                
                ("initializationState", c_int),  # wormInitializationState),
                ]


class Cell(Structure):
    pass

