# Library-Update 6.0

Im Sommer 2026 kam das Upgrade auf Library 6.0 im Vorgriff auf Hardware 2.0, die etwas anders arbeitet.

Das Entwickler-Kit und dessen Dokumentation enthalten eine vollständige Liste der Änderungen

In dieser Library wurden dem Konstruktor die Argumente `admin_pin` und `admin_puk` hinzugefügt. Werden diese hier übergeben, dann kümmert sich die Library vollautomatisch um die Initialisierung des TSE-Moduls. Die Änderung sollte abwärtskompatibel sein. Werden die Parameter nicht übergeben, findet keine automatische Initialisierung statt.

Dann sollte dafür statt meiner bisherigen Erweiterung `tse_prepare()` nun die gleichwertige Funktion `tse_setup_ext()` verwendet werden.
