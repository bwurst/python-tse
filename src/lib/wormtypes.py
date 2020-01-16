from ctypes import POINTER, c_char


# FIXME: Das sollte ein struct sein, wir wissen aber nicht was alles darin sein muss.

WormContext = POINTER(c_char)