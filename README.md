# ralsync
## Podsumowanie
Nowy system emisyjny RA działa aktualnie w systemie tygodniowym. Ramówka znajduje się w odpowiednim spreadsheecie. Dane z tego spreadsheetu są użyte do odpiewdniej konfiguracji Liquidsoapa i Crona.
Głównym elementem jest skrypt synchronizujący **rals.py**, reszta skryptów to skrypty wykonywane przez Crona
## Ogólna działalość skryptów
### rals.py
1. Pobiera tabele ze spreadsheetu
2. Tworzy słowniki dla każdego dnia (slownik[audycja]="HHhMMm - HHhMMm") tygodnia
3. zapisuje napotkane nazwy uproszczone do pliku
4. znajduje "tagi" "#--AUDYCJE" w konfiguracji Liquidsoapa, usuwa wszystko między nimi i tworzy tam odpowiednie wpisy inputów
5. analogicznie dla tagu "#--SWITCH"
6. zapisuje plik konfiguracyjny
7. Na podstawie nazw uproszczonych tworzy pliki dla dodatkowych instancji Liquidsoapa --To jest relikt przeszłości, już nie używany
8. Otwiera tabele Crona użytkownika, czyści ją i tworzy odpowiednie wpisy

### startrec.sh
Przyjmuje ścieżkę do folderu "powtorka" danej audycji, nazwę pliku i nazwę uproszczoną audycji.

1. Tworzy timestamp i umieszcza go w pliku "stamp" + *nazwa uproszczona*
2. Łączy się przez socat do Liquidsoapa i wywołuje polecenie:
dynamic_file.start '/ścieżka do powtórki/wygenerowany timestamp_nazwapliku'

Przyjmowane argumenty są trochę chaotyczne i nie potrzebnie powtarzane ale ostatecznie skrypt służy raczej tylko do automatycznej obsługi
### stoprec.sh
Przyjmuje te same argumenty co startrec.sh

1. Zbiera timestamp z pliku "stamp" + *nazwa uproszczona* 
2. Łączy się przez socat do Liqudisoapa i wywołuje polecenie:
dynamic_file.stop 'ścieżka do powtórki/pobrany timestamp_nazwapliku'

### requestpush.sh
Przyjmuje uproszczoną nazwę audycji i nazwę pliku

1. Łączy się przez socat do Liquidsoapa i wykonuje polecenie:
request_nazwaaudycji.push nazwapliku
2. Zapisuje odpowiedź socata do pliku "request_nazwauproszczona.log"

### requestremove.sh
Przujmuje uproszczoną nazwę audcyji i utwór do usunięcia z kolejki
Łaczy się przez socat do Liquidsoapa i wykonuje polecenie:
request_nazwaaucyji.remove numerutworu
### utworzfolderaudycji.py
1. Czyta nazwy uproszczone audycji z pliku generowanego przez rals.py
2. Próbuje tworzyć foldery każdej z audycji - istniejące pomija

### archiwizacja.py
Przyjmuje nazwę uproszczoną audycji

1. Tworzy liste elementów w folderze "powtorka" danej audycji
2. Jeśli element nie jest folderem to przenosi go do folderu "archiwum" danej audycji
3. Tworzy liste elementów w fodlerze "powtorka/powtorka_puszki" danej audycji
4. Usuwa te elementy

### puszka_przerzut.py
Przyjmuje uproszczoną nazwę audycji

1. Tworzy listę elementów w folderze "puszka" danej audycji
2. Przemieszcza wszystkie elementy do folderu "powtorka_puszki" danej audycji

### requestpowtorki.py
Przyjmuje uproszczoną nazwę audycji

1. Tworzy listę elementów w folderze "powtorka_puszki" danej audycji
2. Sortuje liste
3. Wykonuje "requestpuszki.sh nazwauproszczona ścieżkadopliku" dla każdego pliku na liście
4. Czyta numer utworu z pliku "request_nazwauproszczona.log"
5. Jeżeli lista elementów była pusta to tworzy listę elementów z folderu "powtorka" danej audycji
6. Działa analogicznie jak w przypadku pierwszej listy.
7. Zapisuje zebrane numery utworów do pliku "queue_nazwauproszczona.log"

### requestpuszki.py
Działa analogicznie do requestpowtorki.py ale zbiera pliki z folderu "puszka"

### clean.py
Przyjmuje nazwę uproszczoną audycji

1. Czyta kolejkę utworów z pliku "queue_nazwa uproszczona"
2. Wykonuje "requestremove.sh nazwa_uproszczona numer_utworu" dla każdego utworu

### czyszczenie.py
1. Tworzy liste elementów z folderu "audycje"
2. Dla każdego z folderów próbuje zrobić listę elementów w podfolderze "powtorka"
3. Sprawdza rozmiar każdego z elementów z listy
4. Jeżeli element ma poniżej 30mb zostaje usunięty
5. Nazwy usuniętych plików są zapisywane do pliku "czyszczenie.log"

## Opis funkcji
### rals.py
#### zmianakonca(koniec)
Przyjmuje string z godziną w formacie "HH:MM" i zwraca godzine 30 minut później
#### czasformatls(czas)
Przyjmuje string z godziną w formacie "HH:MM" i zwraca string w formacie "HHhMMm"
#### utworzslownikdnia(values, slownik, kolumna)
Przyjmuje dwuwymiarową listę z danymi ze spreadsheetu ramówki, słownik do zapełnienia i kolumne z której będą zbierane wartości.
W słowniku tworzy klucze z nazw audycji i nadaje im wartości w formacie "HHhMMm - HHhMMm" odpowiadające początkowi i końcu audycji
#### wpisyinputow(slur)
Przyjmuje string z uproszczoną nazwą audycji
Zwraca string z treścią wpisu tworzącego input do konfiguracji Liquidsoapa
#### wpisynagrywania(slur) --Już nie używana
Przyjmuje string z uproszczoną nazwą audycji
Zwraca string z treścią wpisu tworzącego output do konfiguracji Liquidsoapa
#### switchzeslownika(slownik, dzien)
Przyjmuje slownik (slownik[audycja]="HHhMMm - HHhMMm")
Zwraca string z treścią wpisu dla Switcha do konfiguracji Liquidsoapa
#### czasformatcron(string, p, d)
Przyjmuje string z czasem w formacie "HHh:MMm - HHh:MMm" i numery dwóch znaków (
p i d)
Dwa wskazane znaki są zwracane jako int gdzie "p" to rząd dziesiątek a "d" to rząd jedności
#### cronzeslownika(cron, slownik, dzien)
Przyjmuje otwartego Crona, slownik (slownik[audycja]="HHhMMm - HHhMMm") i numer dnia (w systemie Cronowym)
Na podstawie slownika tworzone sa wpisy uruchamiające skrypty:

* archiwizacja.py - 5 minut po końcu powtórki
* requestpowtorki.py - w momencie startu powtórki
* clean.py - 5 minut po końcu powtórki
* requestpuszki.py - w momencie startu audycji
* clean.py - 5 minut po końcu audcyji
* startrec.sh - w momencie startu audycji
* stoprec.sh - w momencie końca audycji
* czyszczenie.py - 3 minuty po końcu audycji
* puszka_przerzut.py - 5 minut po końcu audcyji


