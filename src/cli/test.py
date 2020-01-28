
import config
import sys
import os.path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))


from worm import Worm

worm = Worm()

if len(sys.argv) > 1 and sys.argv[1] == '--info':
    print('Kapazität:', worm.info.capacity)
    print('Development-Firmware? =>', worm.info.isDevelopmentFirmware)
    print('Benutzter Speicher:', worm.info.size)
    
    print('Gültige Zeit gesetzt? =>', worm.info.hasValidTime)
    print('Selbsttest gemacht? =>', worm.info.hasPassedSelfTest)
    print('Ist das CTSS-Interface aktiv? =>', worm.info.isCtssInterfaceActive)
    print('Initialisierungs-Status:', worm.info.initializationState)
    
    print('Transaktion läuft grade? =>', worm.info.isDataImportInProgress)
    
    print('PUK schon gesetzt? =>', worm.info.hasChangedPuk)
    print('Admin-PIN schon gesetzt? =>', worm.info.hasChangedAdminPin)
    print('Time-Admin-PIN schon gesetzt? =>', worm.info.hasChangedTimeAdminPin)
    
    print('Zeit bis zum nächsten Selbsttest:', worm.info.timeUntilNextSelfTest)
    print('Zeit bis zum nächsten Time-Sync:', worm.info.maxTimeSynchronizationDelay)
    print('Maximale Dauer einer offenen Transaktion:', worm.info.maxUpdateDelay)
    
    print('Zahl der offenen Transaktionen: %i / %i' % (worm.info.startedTransactions, worm.info.maxStartedTransactions))
    print('Zahl der bisherigen Signaturen: %i / %i (noch %i übrig)' % (worm.info.createdSignatures, worm.info.maxSignatures, worm.info.remainingSignatures))
    
    print('TSE-Beschreibung:', worm.info.tseDescription)
    print('Signatur-Algorithmus:', worm.signatureAlgorithm())
    print('Pubkey:', worm.info.tsePublicKey)
    print('Serial:', worm.info.tseSerialNumber)
    
    print('Zahl der aktiven Clients: %i / %i' % (worm.info.registeredClients, worm.info.maxRegisteredClients))
    print('Zertifikat-Ablaufdatum:', worm.info.certificateExpirationDate)
    
    print('Hardware-Version: %i.%i.%i' % worm.info.hardwareVersion)
    print('Software-Version: %i.%i.%i' % worm.info.softwareVersion)
    print('Library-Version:', worm.getVersion())
    print('TSE Form-Factor:', worm.info.formFactor)
    
    worm.flash_health_summary()

if len(sys.argv) > 1 and sys.argv[1] == '--reset':
    worm.tse_factoryReset()



#print(worm.runSelfTest()) # läuft (jetzt nicht mehr. Keine Ahnung wieso!!)

#print(worm.user_login())
#print(worm.user_unblock())
#print(worm.user_change_puk())


#print(worm.info_capacity()) # läuft nicht (wahrscheinlich weil WormInfo nicht korrekt definiert ist)

#print(worm.flash_health_summary()) # läuft nicht richtig




