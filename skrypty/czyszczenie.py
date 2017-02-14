import os

path = "/srv/ra/audycje/"

foldery = os.listdir(path)
# print(foldery)

f = open('/home/liquidsoap/czyszczenie.log', 'a')

for folder in foldery:
    try:
        pliki = os.listdir(path + folder + "/powtorka/")
    except OSError:
        continue
    # print(pliki.st_size)
    # print(pliki)
    for plik in pliki:
        try:
            plikstat = os.lstat(path + folder + "/powtorka/" + plik)
        except OSError:
            continue
        # print(plikstat.st_size)
        # print(plikstat.st_mode)
        if plikstat.st_size < 30000000:
            print(plik)
            os.remove(path + folder + "/powtorka/" + plik)
            f.write(plik + ' USUNIETY\n')

f.close()
