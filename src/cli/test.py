import config
import sys
import os.path
from encodings.base64_codec import base64_encode

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))


import worm

myworm = worm.Worm(clientid=config.clientId, time_admin_pin=config.PIN_TIME_ADMIN)

if len(sys.argv) > 1 and sys.argv[1] == '--info':
    print('Kapazität:', myworm.info.capacity)
    print('Development-Firmware? =>', myworm.info.isDevelopmentFirmware)
    print('Benutzter Speicher:', myworm.info.size)
    
    print('Gültige Zeit gesetzt? =>', myworm.info.hasValidTime)
    print('Selbsttest gemacht? =>', myworm.info.hasPassedSelfTest)
    print('Ist das CTSS-Interface aktiv? =>', myworm.info.isCtssInterfaceActive)
    print('Initialisierungs-Status:', myworm.info.initializationState)
    
    print('Transaktion läuft grade? =>', myworm.info.isDataImportInProgress)
    
    print('PUK schon gesetzt? =>', myworm.info.hasChangedPuk)
    print('Admin-PIN schon gesetzt? =>', myworm.info.hasChangedAdminPin)
    print('Time-Admin-PIN schon gesetzt? =>', myworm.info.hasChangedTimeAdminPin)
    
    print('Zeit bis zum nächsten Selbsttest:', myworm.info.timeUntilNextSelfTest)
    print('Zeit zwischen zwei Time-Syncs:', myworm.info.maxTimeSynchronizationDelay)
    print('Maximale Dauer einer offenen Transaktion:', myworm.info.maxUpdateDelay)
    
    print('Zahl der offenen Transaktionen: %i / %i' % (myworm.info.startedTransactions, myworm.info.maxStartedTransactions))
    print('Zahl der bisherigen Signaturen: %i / %i (noch %i übrig)' % (myworm.info.createdSignatures, myworm.info.maxSignatures, myworm.info.remainingSignatures))
    
    print('TSE-Beschreibung:', myworm.info.tseDescription, 'Customization:', myworm.info.customizationIdentifier.decode('ascii'))
    print('Signatur-Algorithmus:', myworm.signatureAlgorithm())
    print('Pubkey:', base64_encode(myworm.info.tsePublicKey))
    print('Serial:', bytes(myworm.info.tseSerialNumber).hex())
    
    print('Zahl der aktiven Clients: %i / %i' % (myworm.info.registeredClients, myworm.info.maxRegisteredClients))
    print('Zertifikat-Ablaufdatum:', myworm.info.certificateExpirationDate)
    
    print('Log-Time-Format:', myworm.logTimeFormat())
    print('Hardware-Version: %i.%i.%i' % myworm.info.hardwareVersion)
    print('Software-Version: %i.%i.%i' % myworm.info.softwareVersion)
    print('Library-Version:', myworm.getVersion())
    print('TSE Form-Factor:', myworm.info.formFactor)
    
    myworm.flash_health_summary()

if len(sys.argv) > 1 and sys.argv[1] == '--reset':
    myworm.tse_factoryReset()

if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
    myworm.tse_runSelfTest()

if len(sys.argv) > 1 and sys.argv[1] == '--setup':
    if not myworm.info.hasPassedSelfTest:
        myworm.tse_runSelfTest()
    myworm.tse_setup('SwissbitSwissbit', config.PUK, config.PIN, config.PIN_TIME_ADMIN)

if len(sys.argv) > 1 and sys.argv[1] == '--time':
    myworm.tse_updateTime()

if len(sys.argv) > 1 and sys.argv[1] == '--login':
    myworm.user_login()

if len(sys.argv) > 1 and sys.argv[1] == '--initcreds':
    myworm.user_deriveInitialCredentials()


if len(sys.argv) > 1 and sys.argv[1] == '--trxstart':
    response = myworm.transaction_start('processdata'.encode('ascii'), 'Bestellung-V1')
    num = response.transactionNumber
    print(num)
    print(response.signatureCounter)
    print(response.logTime)
    response = myworm.transaction_update(num, 'processdata2'.encode('ascii'), 'Bestellung-V1')
    print(response.signatureCounter)
    print(response.logTime)
    response = myworm.transaction_finish(num, 'processdata3'.encode('ascii'), 'Bestellung-V1')
    print(response.signatureCounter)
    print(response.logTime)
    print(base64_encode(response.signature))


if len(sys.argv) > 1 and sys.argv[1] == '--trxlist':
    trx = myworm.transaction_listStartedTransactions(0)
    print(trx)

if len(sys.argv) > 1 and sys.argv[1] == '--trxfinishall':
    trx = myworm.transaction_listStartedTransactions(0)
    for t in trx:
        response = myworm.transaction_finish(t, ''.encode('ascii'), 'Bestellung-V1')
        
if len(sys.argv) > 2 and sys.argv[1] == '--export-tar':
    myworm.export_tar(sys.argv[2])

if len(sys.argv) > 2 and sys.argv[1] == '--export-tar-inc':
    try:
        (firstSignatureCounter, lastSignatureCounter, newState) = myworm.export_tar_incremental(sys.argv[2])
        print('newState:', bytes(newState).hex())
    except worm.WormException as err:
        if err.errno == worm.WORM_ERROR_INCREMENTAL_EXPORT_INVALID_STATE:
            print('Die TSE-Einheit ist nicht bereit für einen Export!')
        else:
            print('Fehler beim Export: %s' % err.errno)

if len(sys.argv) > 1 and sys.argv[1] == '--cert':
    print(myworm.getLogMessageCertificate().decode())

if len(sys.argv) > 1 and sys.argv[1] == '--listentries':
    e = myworm.entry
    myworm.entry.iterate_first()
    while e.isValid:
        print('Transaktion: #%i (%s)' % (e.id, e.type))
        print('  ', e.readLogMessage())
        print('  ', e.readProcessData())
        myworm.entry.iterate_next()
        

#print(myworm.runSelfTest()) # läuft (jetzt nicht mehr. Keine Ahnung wieso!!)

#print(myworm.user_login())
#print(myworm.user_unblock())
#print(myworm.user_change_puk())


#print(myworm.info_capacity()) # läuft nicht (wahrscheinlich weil mywormInfo nicht korrekt definiert ist)

#print(myworm.flash_health_summary()) # läuft nicht richtig




