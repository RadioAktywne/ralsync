import argparse
import os
import pathlib


parser = argparse.ArgumentParser()
parser.add_argument("slur")
args = parser.parse_args()

path = "/srv/ra/audycje/"+args.slur

pliki = os.listdir(path+"/powtorka/")
# print(pliki.st_size)
print(pliki)
for plik in pliki:
    # print(plikstat.st_size)
    pathplik = pathlib.Path(path+"/powtorka/"+plik)
    if pathplik.is_dir() is False:
        os.rename(path + "/powtorka/" + plik, path + "/archiwum/" + plik)
pliki = os.listdir(path+"/powtorka/powtorka_puszki")
for plik in pliki:
    os.remove(path+"/powtorka/powtorka_puszki/"+plik)
