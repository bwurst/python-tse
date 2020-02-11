import config
import sys
import os.path
from encodings.base64_codec import base64_encode

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))


import worm

TSE = worm.Worm(clientid=config.clientId, time_admin_pin=config.PIN_TIME_ADMIN)

if len(sys.argv) > 1 and sys.argv[1] == '--info':
    print('Kapazität:', TSE.info.capacity)
    print('Development-Firmware? =>', TSE.info.isDevelopmentFirmware)
    print('Benutzter Speicher:', TSE.info.size)
    
    print('Gültige Zeit gesetzt? =>', TSE.info.hasValidTime)
    print('Selbsttest gemacht? =>', TSE.info.hasPassedSelfTest)
    print('Ist das CTSS-Interface aktiv? =>', TSE.info.isCtssInterfaceActive)
    print('Initialisierungs-Status:', TSE.info.initializationState)
    
    print('Transaktion läuft grade? =>', TSE.info.isDataImportInProgress)
    
    print('PUK schon gesetzt? =>', TSE.info.hasChangedPuk)
    print('Admin-PIN schon gesetzt? =>', TSE.info.hasChangedAdminPin)
    print('Time-Admin-PIN schon gesetzt? =>', TSE.info.hasChangedTimeAdminPin)
    
    print('Zeit bis zum nächsten Selbsttest:', TSE.info.timeUntilNextSelfTest)
    print('Zeit zwischen zwei Time-Syncs:', TSE.info.maxTimeSynchronizationDelay)
    print('Maximale Dauer einer offenen Transaktion:', TSE.info.maxUpdateDelay)
    
    print('Zahl der offenen Transaktionen: %i / %i' % (TSE.info.startedTransactions, TSE.info.maxStartedTransactions))
    print('Zahl der bisherigen Signaturen: %i / %i (noch %i übrig)' % (TSE.info.createdSignatures, TSE.info.maxSignatures, TSE.info.remainingSignatures))
    
    print('TSE-Beschreibung:', TSE.info.tseDescription, 'Customization:', TSE.info.customizationIdentifier.decode('ascii'))
    print('Signatur-Algorithmus:', TSE.signatureAlgorithm())
    print('Pubkey:', base64_encode(TSE.info.tsePublicKey))
    print('Serial:', bytes(TSE.info.tseSerialNumber).hex())
    
    print('Zahl der aktiven Clients: %i / %i' % (TSE.info.registeredClients, TSE.info.maxRegisteredClients))
    print('Zertifikat-Ablaufdatum:', TSE.info.certificateExpirationDate)
    
    print('Log-Time-Format:', TSE.logTimeFormat())
    print('Hardware-Version: %i.%i.%i' % TSE.info.hardwareVersion)
    print('Software-Version: %i.%i.%i' % TSE.info.softwareVersion)
    print('Library-Version:', TSE.getVersion())
    print('TSE Form-Factor:', TSE.info.formFactor)
    
    TSE.flash_health_summary()

if len(sys.argv) > 1 and sys.argv[1] == '--reset':
    TSE.tse_factoryReset()

if len(sys.argv) > 1 and sys.argv[1] == '--prepare':
    TSE.tse_prepare(config.PUK, config.PIN)

if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
    TSE.tse_runSelfTest()

if len(sys.argv) > 1 and sys.argv[1] == '--registerclient':
    TSE.user_login(worm.WORM_USER_ADMIN, config.PIN)
    TSE.tse_registerClient()

if len(sys.argv) > 1 and sys.argv[1] == '--deregisterclient':
    TSE.user_login(worm.WORM_USER_ADMIN, config.PIN)
    TSE.tse_deregisterClient()

if len(sys.argv) > 1 and sys.argv[1] == '--clients':
    TSE.user_login(worm.WORM_USER_ADMIN, config.PIN)
    clients = TSE.tse_listRegisteredClients()
    print('registrierte Clients:')
    for c in clients:
        print('- '+c)

if len(sys.argv) > 1 and sys.argv[1] == '--setup':
    TSE.tse_setup(config.PUK, config.PIN, config.PIN_TIME_ADMIN)

if len(sys.argv) > 1 and sys.argv[1] == '--time':
    TSE.tse_updateTime()

if len(sys.argv) > 1 and sys.argv[1] == '--login':
    TSE.user_login(worm.WORM_USER_ADMIN, config.PIN)

if len(sys.argv) > 1 and sys.argv[1] == '--initcreds':
    print(TSE.user_deriveInitialCredentials())


if len(sys.argv) > 1 and sys.argv[1] == '--trxstart':
    response = TSE.transaction_start('processdata', 'Bestellung-V1')
    num = response.transactionNumber
    print(num)
    print(response.signatureCounter)
    print(response.logTime)
    response = TSE.transaction_update(num, 'processdata2'.encode('ascii'), 'Bestellung-V1')
    print(response.signatureCounter)
    print(response.logTime)
    response = TSE.transaction_finish(num, 'processdata3'.encode('ascii'), 'Bestellung-V1')
    print(response.signatureCounter)
    print(response.logTime)
    print(base64_encode(response.signature))


if len(sys.argv) > 1 and sys.argv[1] == '--trxlist':
    trx = TSE.transaction_listStartedTransactions(0)
    print(trx)

if len(sys.argv) > 1 and sys.argv[1] == '--trxfinishall':
    trx = TSE.transaction_listStartedTransactions(0)
    for t in trx:
        response = TSE.transaction_finish(t, ''.encode('ascii'), 'Bestellung-V1')
        
if len(sys.argv) > 2 and sys.argv[1] == '--export-tar':
    TSE.export_tar(sys.argv[2])

if len(sys.argv) > 2 and sys.argv[1] == '--export-tar-inc':
    try:
        (firstSignatureCounter, lastSignatureCounter, newState) = TSE.export_tar_incremental(sys.argv[2])
        print('newState:', bytes(newState).hex())
    except worm.WormException as err:
        if err.errno == worm.WORM_ERROR_INCREMENTAL_EXPORT_INVALID_STATE:
            print('Die TSE-Einheit ist nicht bereit für einen Export!')
        else:
            print('Fehler beim Export: %s' % err.errno)

if len(sys.argv) > 1 and sys.argv[1] == '--cert':
    print(TSE.getLogMessageCertificate().decode())

if len(sys.argv) > 1 and sys.argv[1] == '--listentries':
    e = TSE.entry
    TSE.entry.iterate_first()
    while e.isValid:
        print('Transaktion: #%i (%s)' % (e.id, e.type))
        print('  ', e.readLogMessage())
        print('  ', e.readProcessData())
        TSE.entry.iterate_next()
        

#print(TSE.runSelfTest()) # läuft (jetzt nicht mehr. Keine Ahnung wieso!!)

#print(TSE.user_login())
#print(TSE.user_unblock())
#print(TSE.user_change_puk())


#print(TSE.info_capacity()) # läuft nicht (wahrscheinlich weil mywormInfo nicht korrekt definiert ist)

#print(TSE.flash_health_summary()) # läuft nicht richtig




