
import config
import sys

sys.path.append(config.path_lib)


from worm import Worm

worm = Worm(config.path_tse)

#print(worm.getVersion()) # läuft
#print(worm.signatureAlgorithm()) # läuft


worm.info_read() # läuft nicht richtig (wahrscheinlich weil WormInfo nicht korrekt definiert ist)

print('Kapazität:', worm.info_capacity())
print('Development-Firmware? =>', worm.info_isDevelopmentFirmware())
print('Benutzter Speicher:', worm.info_size())

print('Gültige Zeit gesetzt? =>', worm.info_hasValidTime())
print('Selbsttest gemacht? =>', worm.info_hasPassedSelfTest())
print('Ist das CTSS-Interface aktiv? =>', worm.info_isCtssInterfaceActive())

#print(worm.runSelfTest()) # läuft (jetzt nicht mehr. Keine Ahnung wieso!!)

#print(worm.user_login())
#print(worm.user_unblock())
#print(worm.user_change_puk())


#print(worm.info_capacity()) # läuft nicht (wahrscheinlich weil WormInfo nicht korrekt definiert ist)

#print(worm.flash_health_summary()) # läuft nicht richtig




