# python-tse
Gemäß KassenSicherungsVerordnung muss jede in Deutschland betriebene Bargeld-Registrierkasse ab 2020 mit einem Sicherheitsmodul "TSE" / "Technische Sicherheits-Einrichtung" ausgerüstet werden. Ein Hersteller dieser Geräte ist die schweizerische Firma Swissbit.

Voraussetzung für die Nutzung dieses Moduls ist eine binäre Bibliothek, die mit der TSE kommuniziert. Die Weitergabe-Auflagen dieser Bibliothek sind restriktiv, daher ist diese Bibliothek nicht hier im Repository enthalten. Käufer der Entwickler-Version erhalten diese Daten vom Händler.

Der Interne Name der TSE-Bibliothek ist **worm** ("write once, read many"), der aus Gründen der Kompatibilität beibehalten wird. 

Diese Python-Bibliothek kümmert sich um den Datenaustausch mit dem Modul.

Im Programm **cli/test.py** befinden sich Anwendungsbeispiele für die Nutzung aller Funktionen.

Zum Zugriff auf das TSE-Modul ist eine "Client-ID" nötig, die das Kassensystem identifiziert. Das kann ein beliebiger Freitext sein, also alphanumerisch. Intern wird dieser String als "latin1" codiert. Es wird dringend empfohlen, sich auf die einfachen ASCII-Zeichen zu beschränken. Das TSE-Modul kann mehrere Client-IDs verwalten und parallel betreiben, das ist in dieser Bibliothek aber nicht implementiert.

Das Modul kennt 3 Zugangsdaten: Admin-PIN (5-stellig, für Aktivierung/Deaktivierung und ähnliches), Time-Admin-PIN (5-stelling, zum aktualisieren der Zeit) und Admin-PUK (6-stellig) um die anderen PINs wieder freizuschalten. Die Zeit muss regelmäßig (ca. alle halbe Stunde) neu gesetzt werden, daher muss diese PIN im Regelbetrieb zur Verfügung stehen. 

Ein Ablauf könnte so aussehen:

## Nutzung der Bibliothek

```python
import worm

tse = worm.Worm(clientid="...", time_admin_pin="...")
```

Bei einem fabrikneuen Modul wird dann eine Warnung ausgegeben, dass das Modul noch nicht initialisiert ist.

```
./src/lib/worm.py:54: Warning: TSE ist noch nicht initialisiert. Bitte zuerst initialisieren!
  warnings.warn(Warning('TSE ist noch nicht initialisiert. Bitte zuerst initialisieren!'))
```


## Einmaliges Initialisieren der TSE

Vor der allerersten Nutzung muss die TSE initialisiert werden. Ob dies nötig ist, zeigt die Status-Variable **initializationState**.

```python
if tse.info.initializationState == worm.WORM_INIT_UNINITIALIZED:
	tse.tse_setup('SwissbitSwissbit', adminpuk=ADMIN_PUK, adminpin=ADMIN_PIN, timeadminpin=TIME_ADMIN_PIN)
```
Die PINs und die PUK müssen dabei alle vom Anwendungssystem bereitgestellt werden. Die Client-ID sollte bereits im Konstruktor übergeben worden sein und wird aus diesem verwendet.

Die Swissbit-Bibliothek unterstützt einige Kommandos um die Initialisierung einzeln vorzunehmen. Diese sind hier nicht implementiert, da alles mit einem einzigen Aufruf von tse_setup() erledigt wird. 


## Selbsttest und Zeit

Nach einem Neustart und nach mehr als 24 Stunden Betrieb muss das TSE-Modul einen Selbsttest machen, zudm muss regelmäßig ca. alle halbe Stunde die Zeit gesetzt werden. Beides macht die Python-Bibliothek transparent bei Bedarf um Transaktionen zu ermöglichen. **HINWEIS:** Da der Selbsttest bis zu einer Minute dauern kann, ist es sinnvoll, den Selbsttest beim Start und danach täglich zu machen bevor eine Kunden-Transaktion eröffnet wird. Das Setzen der Zeit ist unerheblich und kann automatisch bei Bedarf erfolgen.

```python
if not tse.info.hasPassedSelfTest:
	tse.tse_runSelfTest()
if not tse.info.hasValidTime:
	tse.tse_updateTime()
```

## Transaktionen

Um Kassen-Transaktionen abzusichern muss eine Transaktion gestartet, beliebig oft aktualisiert und beendet werden. Die Aktualisierung kann ausbleiben wenn keine Änderungen mehr nötig sind. Start und Beenden ist obligatorisch.

Bei diesen Operationen wird ein "response"-Objekt zurückgegeben, aus dem Status-Informationen ausgelesen werden können. Die Transaktionsnummer ist dabei besonders wichtig für die nachfolgenden Operationen.

```python
response = myworm.transaction_start(processdata=b'...', processtype='Bestellung-V1')
num = response.transactionNumber
response = myworm.transaction_update(num, processdata=b'...', processtype='Bestellung-V1')
response = myworm.transaction_finish(num, processdata=b'...', processtype='Bestellung-V1')

print(response.signatureCounter)
print(response.logTime)
print(base64_encode(response.signature))
```

Hier wird eine Transaktion gestartet, einmal aktualisiert und danach abgeschlossen. Am Ende werden der Signatur-Zähler, die Signatur-Zeit und die Signatur ausgegeben.

Die Parameter **processtype** und **processdata** sollten als Bytes-Objekte übergeben werden um Verfälschungen auszuschließen. Hilfsweise werden Strings via "latin1"-Codec codiert.

## Exceptions

Wenn ein Fehler auftritt, wird dieser als "worm.WormException" geworfen und kann wie folgt behandelt werden.

```python
try:
    tse.start_transaction(...)
except worm.WormException as e:
    print(e.errno)
    print(e.message) 
```
Für errno stehen die Konstanten aus der Entwickler-Doku zur Verfügung.


## TAR-Export

Für Kassenprüfungen und zu Dokumentationszwecken muss der Bestand in der TSE immer wieder exportiert werden. Dafür stehen mehrere Routinen zur Verfügung:

```python
tse.export_tar(filename='...')
```
Hier wird der gesamte Bestand als ein TAR-File exportiert. Es können Einschränkungen nach Datum oder Transaktionenummern festgelegt werden, Details sind im Code nachzuschauen.

```python
(firstSignatureCounter, lastSignatureCounter, newState) = tse.export_tar_incremental(filename='...', lastState=None)
```
Hier wird Status als "newState" ausgegeben, dieser kann beim nächsten Aufruf als "lastState" wieder übergeben werden um den Export ab der letzten Steller weiter zu führen. Der Status muss dabei vom Kassensystem zwischengespeichert werden um z.B. einen täglichen oder wöchentlichen inkrementellen Export zu machen. 


## Abrufen der Transaktionen

FIXME: Wie das in der Praxis benutzt wird, weiß keiner...

```python
e = tse.entry
tse.entry.iterate_first()
while e.isValid:
    print('Transaktion: #%i (%s)' % (e.id, e.type))
    print('  ', e.readLogMessage())
    print('  ', e.readProcessData())
    tse.entry.iterate_next()
```