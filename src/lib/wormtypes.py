from ctypes import *

WormContext = c_void_p
WormInfo = c_void_p
WormError = c_int



(WORM_INIT_UNINITIALIZED,
WORM_INIT_INITIALIZED,
WORM_INIT_DECOMMISSIONED) = range(3)




# constants for WormUserId
WORM_USER_UNAUTHENTICATED = 0
WORM_USER_ADMIN = 1
WORM_USER_TIME_ADMIN = 2



