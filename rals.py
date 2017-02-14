from __future__ import print_function
import httplib2
import os
from crontab import CronTab

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from utworzfolderaudycji import utworz_folder_audycji

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

pos1 = 0
pos2 = 0


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'ralssynch.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def zmianakonca(koniec):
    koniec = list(koniec)
    if koniec[3] == '3':
        if koniec[1] == '9':
            if koniec[0] == '0':
                koniec[0] = '1'
            else:
                koniec[0] = '2'
            koniec[1] = '0'
        else:
            koniec[1] = str(int(koniec[1])+1)
        koniec[3] = '0'

    elif koniec[3] == '0':
        koniec[3] = '3'
    koniec = ''.join(koniec)
    return koniec


def czasformatls(czas):
    czas = list(czas)
    czas[2] = 'h'
    czas.append('m')
    czas = ''.join(czas)
    return czas


slury = []


def utworzslownikdnia(values, slownik, kolumna):
    ostatni = ''
    koniec = ''
    poczatek = ''
    if not values:
        print('No data found.')
    else:
        for row in values:
            # print(row)
            # print(ostatni)
            if ostatni != row[kolumna]:
                if ostatni != '':
                    ostatni2 = ostatni.replace("_p", "")
                    # print(ostatni)
                    # print(ostatni2)
                    if ostatni2 not in slury:
                        # print(ostatni2)
                        slury.append(ostatni2)
                    if ostatni in slownik:
                        ostatni = list(ostatni)
                        ostatni.append('1')
                        ostatni = ''.join(ostatni)
                    slownik[ostatni] = (czasformatls(poczatek)
                                        + ' - '
                                        + czasformatls(zmianakonca(koniec)))

                ostatni = row[kolumna]
                poczatek = row[0]
            koniec = row[0]


def wpisyinputow(slur):
    lista = ['#' + slur + '\n',
             'request_' + slur + ' = request.equeue(id="request_'
             + slur + '")\n', slur + ' = fallback(track_sensitive=false, '
             + '[request_' + slur + ', studio, muzyka])\n']
    if (("grabek" not in slur) and
            ("plytatygodnia" not in slur) and
            ("gnp" not in slur)):
        lista.append(slur + "_p = fallback(track_sensitive=false, [request_"
                     + slur + ", muzyka])\n")
    lista.append("#" + slur + "\n")
    return lista


def wpisynagrywania(slur):
    lista = ['#' + slur + '\n',
             'nagrywanie_' + slur + ' = output.file(%vorbis,\n',
             '"/srv/ra/audycje/'+slur+'/powtorka/'
             + slur + '_#{time_stamp}.ogg",\n',
             'fallible=true,\n', 'reopen_delay=128.0,\n',
             'start=true\n', 'live_' + slur, ')\n', '#' + slur + '\n']
    return lista


def switchzeslownika(slownik, dzien):
    temp = []
    for a in slownik.keys():
        if 'Playlista' not in a:
            # slur = list(a)
            slur2 = a
            if '_p' in a:
                # slur2 = a.replace("_p","")
                # slur2 = ''.join(slur)
                temp.append('({(' + dzien + 'w) and '
                            + slownik[a] + '}, ' + slur2 + '),\n')
            else:
                temp.append('({(' + dzien + 'w) and '
                            + slownik[a] + '}, ' + slur2 + '),\n')
    return temp


def czasformatcron(string, p, d):
    tmp = []
    tmp.append(string[p])
    tmp.append(string[d])
    zmienna = "".join(tmp)
    zmienna = int(zmienna)
    return zmienna


def cronzeslownika(cron, slownik, dzien):

    hp = 0
    mp = 0
    hk = 0
    mk = 0
    dzienk = dzien
    for key in slownik.keys():
        if "Playlista" in key:
            continue
        dzienk = dzien
        hp = czasformatcron(slownik[key], 0, 1)
        mp = czasformatcron(slownik[key], 3, 4)
        hk = czasformatcron(slownik[key], 9, 10)
        mk = czasformatcron(slownik[key], 12, 13)
        if hk is 24:
            hk = 0
            if dzien is '6':
                dzienk = '0'
            else:
                dzienk = str(int(dzien)+1)
        if "_p" in key:
            slur = key.replace("_p", "")
            comm = "python3 /home/liquidsoap/skrypty/archiwizacja.py " + slur
            job = cron.new(command=comm, comment="Archiwizacja")
            czas = str(mk+5) + " " + str(hk) + " * * " + dzienk
            job.setall(czas)
            # REQUEST POWTORKI
            comm = ("python3 /home/liquidsoap/skrypty/requestpowtorki.py "
                    + slur)
            job = cron.new(command=comm, comment="Request Powtorki")
            czas = str(mp) + " " + str(hp) + " * * " + dzien
            job.setall(czas)
            comm = "python3 /home/liquidsoap/skrypty/clean.py " + slur
            job = cron.new(command=comm, comment="Request Czyszczenie")
            czas = str(mk+5) + " " + str(hk) + " * * " + dzienk
            job.setall(czas)
        else:
            slur = key
            # NAGRYWANIE STARE
            # comm = "liquidsoap /etc/liquidsoap/" + slur + "_rec.liq"
            # job = cron.new(command=comm, comment="Uruchomienie nagrywania")
            # czas = str(mp) + " " + str(hp) + " * * " + dzien
            # job.setall(czas)
            # comm = ('kill `ps -ef | grep "/etc/liquidsoap/'
            #         + slur + '_rec.liq" '
            #         + "| grep -v grep | grep -v '/bin/sh' "
            #         + "| awk '{print $2}'`")
            # job = cron.new(command=comm, comment="Wylaczenie nagrywania")
            # czas = str(mk) + " " + str(hk) + " * * " + dzienk
            # job.setall(czas)
            # comm = 'python3 /home/liquidsoap/skrypty/czyszczenie.py'
            # job = cron.new(command=comm, comment="Czyszczenie")
            # czas = str(mk+5) + " " + str(hk) + " * * " + dzienk
            # job.setall(czas)
            #
            # REQUEST PUSZKI
            comm = "python3 /home/liquidsoap/skrypty/requestpuszki.py " + slur
            job = cron.new(command=comm, comment="Request Puszki")
            czas = str(mp) + " " + str(hp) + " * * " + dzien
            job.setall(czas)
            comm = "python3 /home/liquidsoap/skrypty/clean.py " + slur
            job = cron.new(command=comm, comment="Request Czyszczenie")
            czas = str(mk+5) + " " + str(hk) + " * * " + dzienk
            job.setall(czas)
            # NAGRYWANIE NOWE
            comm = ("/home/liquidsoap/startrec.sh /srv/ra/audycje/"
                    + slur + "/powtorka/ " + slur + ".ogg " + slur)
            job = cron.new(command=comm, comment="Uruchomienie nagrywania")
            czas = str(mp) + " " + str(hp) + " * * " + dzien
            job.setall(czas)
            comm = ("/home/liquidsoap/stoprec.sh /srv/ra/audycje/"
                    + slur + "/powtorka/ " + slur + ".ogg " + slur)
            job = cron.new(command=comm, comment="Wylaczenie nagrywania")
            czas = str(mk) + " " + str(hk) + " * * " + dzienk
            job.setall(czas)
            comm = 'python3 /home/liquidsoap/skrypty/czyszczenie.py'
            job = cron.new(command=comm, comment="Czyszczenie")
            czas = str(mk+3) + " " + str(hk) + " * * " + dzienk
            job.setall(czas)
            # PRZERZUT PUSZKI
            comm = ("python3 /home/liquidsoap/skrypty/puszka_przerzut.py "
                    + slur)
            job = cron.new(command=comm, comment="Przerzut puszki")
            czas = str(mk+5) + " " + str(hk) + " * * " + dzienk
            job.setall(czas)
    cron.write()


def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1xm5rDlxo6YlnIQjQRubALrVTtagnqorUIpues5ud0ng'
    rangeName = 'Arkusz1!A1:H49'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    poniedzialek = {}
    wtorek = {}
    sroda = {}
    czwartek = {}
    piatek = {}
    sobota = {}
    niedziela = {}

    utworzslownikdnia(values, poniedzialek, 1)
    utworzslownikdnia(values, wtorek, 2)
    utworzslownikdnia(values, sroda, 3)
    utworzslownikdnia(values, czwartek, 4)
    utworzslownikdnia(values, piatek, 5)
    utworzslownikdnia(values, sobota, 6)
    utworzslownikdnia(values, niedziela, 7)
    print(niedziela)
    print(sroda)
    slurfile = open("/home/liquidsoap/slury", 'w')
    tmpslury = []
    for slur in slury:
        slur = list(slur)
        slur.append('\n')
        slur = ''.join(slur)
        tmpslury.append(slur)
    slurfile.writelines(tmpslury)
    slurfile.close()
    # leci do #--AUDYCJE i czysci miedzy tym a nastepnym tagiem
    # leci aż do #--AUDYCJE i robi z templatki i listy slurow
    # leci do Switcha
    # czyści go
    # leci po slownikach i dorabia wpisy
    # leci do nagrywania
    # czysci
    # dorabia wpisy z listy slurow

    plik = open("/etc/liquidsoap/ra.liq", 'r')

    linijki = plik.readlines()
    # print(linijki)
    plik.close()
    pos1 = 0
    pos2 = 0
    for a in range(0, len(linijki)):
        if linijki[a] == "#--AUDYCJE\n" and pos1 == 0:
            pos1 = a+1
        elif linijki[a] == "#--AUDYCJE\n" and pos1 != 0:
            pos2 = a-1
            break
    if pos1 != pos2:
        while(pos2 - pos1 != 0):
            linijki.pop(pos1)
            pos2 -= 1
    for slur in slury:
        if slur! = 'Playlista':
            temp = wpisyinputow(slur)
            for x in range(0, len(temp)):
                linijki.insert(pos1 + x, temp[x])
    temp1 = pos1
    pos1 = 0
    pos2 = 0

    for a in range(temp1, len(linijki)):
        if linijki[a] == "#--SWITCH\n" and pos1 == 0:
            pos1 = a+1
        elif linijki[a] == "#--SWITCH\n" and pos1 != 0:
            pos2 = a-1
            break
    if pos1 != pos2:
        while(pos2 - pos1 != 0):
            linijki.pop(pos1)
            pos2 -= 1

    temp = switchzeslownika(niedziela, '7')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])
    temp = switchzeslownika(sobota, '6')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])
    temp = switchzeslownika(piatek, '5')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])
    temp = switchzeslownika(czwartek, '4')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])
    temp = switchzeslownika(sroda, '3')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])
    temp = switchzeslownika(wtorek, '2')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])
    temp = switchzeslownika(poniedzialek, '1')
    for a in range(0, len(temp)):
        linijki.insert(pos1 + a, temp[a])

    pos1 = 0
    pos2 = 0

    plik = open("/etc/liquidsoap/ra.liq", 'w')

    plik.writelines(linijki)
    plik.close()
    marker1 = False
    marker2 = False

    for slur in slury:
        config = ['set("log.file.path", "/var/log/liquidsoap/'
                  + slur + '_rec.log")\n',
                  "time_stamp = '%m-%d-%Y, %H:%M:%S'\n",
                  'studio = input.harbor("nagrywanie", '
                  + 'user="USR", password="PASS", port=PORT)\n',
                  'output.file(%vorbis, "/srv/ra/audycje/'
                  + slur + '/powtorka/' + slur
                  + '_#{time_stamp}.ogg", fallible=true, '
                  + 'start=true, studio)\n']
        plyk = open("/etc/liquidsoap/" + slur + "_rec.liq", "w")
        plyk.writelines(config)
        plyk.close()

    # print(linijki)
    # pos=0

    # while marker2:
    # for slur in slury:
    #     if slur!="Playlista":
    #         utworz_folder_audycji(slur)

    cron = CronTab(user=True)
    cron.remove_all()
    cronzeslownika(cron, poniedzialek, '1')
    cronzeslownika(cron, wtorek, '2')
    cronzeslownika(cron, sroda, '3')
    cronzeslownika(cron, czwartek, '4')
    cronzeslownika(cron, piatek, '5')
    cronzeslownika(cron, sobota, '6')
    cronzeslownika(cron, niedziela, '0')

# print(poniedzialek)
# print(wtorek)
# print(sroda)
# print(czwartek)
# print(piatek)
# print(sobota)
# print(niedziela)
# print(slury)
if __name__ == '__main__':
    main()
