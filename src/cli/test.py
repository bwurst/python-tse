
import config
import sys
import os.path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))


from worm import Worm

worm = Worm()

#print(worm.getVersion()) # läuft
#print(worm.signatureAlgorithm()) # läuft


worm.info_read() # läuft nicht richtig (wahrscheinlich weil WormInfo nicht korrekt definiert ist)

print('Kapazität:', worm.info_capacity())
print('Development-Firmware? =>', worm.info_isDevelopmentFirmware())
print('Benutzter Speicher:', worm.info_size())

print('Gültige Zeit gesetzt? =>', worm.info_hasValidTime())
print('Selbsttest gemacht? =>', worm.info_hasPassedSelfTest())
print('Ist das CTSS-Interface aktiv? =>', worm.info_isCtssInterfaceActive())
print('Initialisierungs-Status:', worm.info_initializationState())

print('Transaktion läuft grade? =>', worm.info_isDataImportInProgress())

print('PUK schon gesetzt? =>', worm.info_hasChangedPuk())
print('Admin-PIN schon gesetzt? =>', worm.info_hasChangedAdminPin())
print('Time-Admin-PIN schon gesetzt? =>', worm.info_hasChangedTimeAdminPin())

print('Zeit bis zum nächsten Selbsttest:', worm.info_timeUntilNextSelfTest())
print('Zeit bis zum nächsten Time-Sync:', worm.info_maxTimeSynchronizationDelay())
print('Maximale Dauer einer offenen Transaktion:', worm.info_maxUpdateDelay())

print('Zahl der offenen Transaktionen: %i / %i' % (worm.info_startedTransactions(), worm.info_maxStartedTransactions()))
print('Zahl der bisherigen Signaturen: %i / %i (noch %i übrig)' % (worm.info_createdSignatures(), worm.info_maxSignatures(), worm.info_remainingSignatures()))

print('TSE-Beschreibung:', worm.info_tseDescription())
print('Pubkey:', worm.info_tsePublicKey())
print('Serial:', worm.info_tseSerialNumber())

print('Zahl der aktiven Clients: %i / %i' % (worm.info_registeredClients(), worm.info_maxRegisteredClients()))
print('Zertifikat-Ablaufdatum:', worm.info_certificateExpirationDate())

print('Hardware-Version: %i.%i.%i' % worm.info_hardwareVersion())
print('Software-Version: %i.%i.%i' % worm.info_softwareVersion())
print('TSE Form-Factor:', worm.info_formFactor())



#print(worm.runSelfTest()) # läuft (jetzt nicht mehr. Keine Ahnung wieso!!)

#print(worm.user_login())
#print(worm.user_unblock())
#print(worm.user_change_puk())


#print(worm.info_capacity()) # läuft nicht (wahrscheinlich weil WormInfo nicht korrekt definiert ist)

#print(worm.flash_health_summary()) # läuft nicht richtig




