from ctypes import *

# Das ist nur der Pointer auf ein struct
#WormContext1 = pointer(c_void_p())

#class WormContext(pointer(c_int)):
#    pass

#WormContext = pointer(c_int())

# class WormContext():
#     ctx = pointer(c_int())
#     type = POINTER(type(ctx))

class WormContext(Structure):
    pass

#WormContext = c_void_p
#WormContext = Structure


class WormInitializationState():
    (WORM_INIT_UNINITIALIZED,
    WORM_INIT_INITIALIZED,
    WORM_INIT_DECOMMISSIONED) = map(c_int, range(3))




class WormInfo(Structure):
    
    wormInitializationState = WormInitializationState() # FIXME: das funktionert so noch nicht

    _fields_ = [
                ("customizationIdentifier", c_ubyte), # original: std::vector< unsigned char >
                ("isDevelopmentFirmware", c_bool),
                ("capacity", c_uint32),
                ("size", c_int32),
                ("hasValidTime", c_bool),
                ("hasPassedSelfTest", c_bool),
                ("isCtssInterfaceActive", c_bool),
                ("isExportEnabledIfCspTestFails", c_bool),
                ("initializationState", c_int),  # wormInitializationState),
                ("isDataImportInProgress", c_bool),
                ("hasChangedPuk", c_bool),
                ("hasChangedAdminPin", c_bool),
                ("hasChangedTimeAdminPin", c_bool),
                ("timeUntilNextSelfTest", c_uint32),
                ("startedTransactions", c_uint32),
                ("maxStartedTransactions", c_uint32),
                ("createdSignatures", c_uint32),
                ("maxSignatures", c_uint32),
                ("remainingSignatures", c_uint32),
                ("maxTimeSynchronizationDelay", c_uint32),
                ("maxUpdateDelay", c_uint32),
                ("tsePublicKey", c_ubyte), # original: std::vector< unsigned char >
                ("tseSerialNumber", c_ubyte), # original: std::vector< unsigned char >
                ("tseDescription", c_wchar_p),  # original: std::string
                ("registeredClients", c_uint32),
                ("maxRegisteredClients", c_uint32),
                ("certificateExpirationDate", c_uint64),
                ("tarExportSizeInSectors", c_uint64),
                ("tarExportSize", c_uint64),
                ("hardwareVersion", c_uint32),
                ("softwareVersion", c_uint32),
                ("formFactor", c_wchar_p),  # original: std::string
                ]


WormError = c_int


# constants for WormUserId
WORM_USER_UNAUTHENTICATED = 0
WORM_USER_ADMIN = 1
WORM_USER_TIME_ADMIN = 2





