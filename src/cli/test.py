
import config
import sys

sys.path.append(config.path_lib)


from worm import Worm

worm = Worm(config.path_tse)

#print(worm.getVersion())
#print(worm.signatureAlgorithm())

print(worm.info_read())
#print(worm.info_capacity()) # läuft nicht (wahrscheinlich weil WormInfo nicht korrekt definiert ist)

#print(worm.flash_health_summary()) # läuft nicht richtig




