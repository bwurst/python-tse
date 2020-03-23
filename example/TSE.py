# TSE Implementation Example
# Copyright (C) 2020 Bernd Wurst <bernd@mosterei-wurst.de>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#######################################
#
# Diese Datei stellt eine Klasse dar, die als Singleton Teil einer Anwendung sein kann.
# Dabei wird die TSE-Biobliothek nur einmal instanziert und als neuer Thread gestartet
# und bei weiterer Instanzierung wieder verwendet.
# 
# Zudem wird bei Bedarf selbstständig der Selftest und das Setzen der Zeit vorgenommen.
#
#######################################



import os.path
conf['library'] = os.path.join(os.path.dirname(__file__), '../src/lib')
conf['clientid'] = 'MeineFirma'
conf['timeadminpin'] = '98765'
conf['adminpin'] = '12345'
conf['adminpuk'] = '123456'

from threading import Timer, Thread, Lock, Event
import sys
import time
import logging
sys.path.insert(0, conf['library'])
import worm

TSEException = worm.WormException
log = logging.getLogger(__name__)

class TSE():
    _tse = None
    _thread = None
    _stop = None
    _lock = None
    
    def __init__(self):
        self.master = False
        if not self.__class__._tse:
            log.info('start new TSE controller thread!')
            self.__class__._tse = worm.Worm(clientid=conf['clientid'], time_admin_pin=conf['timeadminpin'])
            self.__class__._lock = Lock()
            self.__class__._stop = Event()
            self.__class__._thread = Thread(target=self.worker)
            self.__class__._thread.start()
            self.master = True

    def worker(self):
        log.debug('this is the new TSE worker thread!')
        while not self.__class__._stop.is_set():
            log.debug('TSE: keep alive!')
            self.keepalive()
            try:
                timeout = 1500
                if not self.__class__._tse.info:
                    # Wenn die TSE nicht da ist, alle Minute prüfen
                    timeout = 60
                self.__class__._stop.wait(timeout)
            except TimeoutError:
                # 25 Minuten vorüber
                pass
        log.debug('TSE worker fertig.')
            
    def keepalive(self):
        with self.__class__._lock:
            try:
                if not self.__class__._tse or not self.__class__._tse.info:
                    log.debug('TSE war nicht korrekt initialisiert')
                    # TSE beim Start nicht vorhanden gewesen!
                    self.__class__._tse = worm.Worm(clientid=conf['clientid'], time_admin_pin=conf['timeadminpin'])
                    self.tse_prepare(adminpuk=conf['adminpuk'], adminpin=conf['adminpin'])
                if not self.info.hasPassedSelfTest or self.info.timeUntilNextSelfTest < 1500:
                    log.debug('TSE-Selbsttest ist jetzt nötig')
                    self.tse_runSelfTest()
                self.tse_updateTime()
            except TSEException as e:
                if e.errno == 2: # TSE nicht verfügbar
                    log.info('Keine TSE vorhanden')
                    pass
                elif e.errno == 0x1011: # client not registered
                    log.info('Die TSE meldet, dass diese Client-ID bisher nicht registriert ist')
                    self.tse_prepare(adminpuk=conf['adminpuk'], adminpin=conf['adminpin'])
        
            
    def __del__(self):
        if self.master:
            self.stop()
        else:
            log.debug('TSE: Beende nicht-master-objekt')

    def stop(self):
        log.debug('TSE: Signalisiere beenden')
        self.__class__._stop.set()

            
    def __getattr__(self, name):
        log.debug('TSE attribute fetched: %s' % (name,))
        return getattr(self.__class__._tse, name)


if __name__ == '__main__':
    tse = TSE()
    print('Signaturzähler: %s' % tse.info.createdSignatures)
    tse2 = TSE()
    print('Signaturzähler: %s' % tse2.info.createdSignatures)
    del(tse)
    del(tse2)