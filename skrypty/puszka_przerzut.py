import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument("slur")
args = parser.parse_args()

path = "/srv/ra/audycje/" + args.slur

pliki = os.listdir(path + "/puszka")
# print(pliki.st_size)
print(pliki)
for plik in pliki:
    # print(plikstat.st_size)
    os.rename(path + "/puszka/" + plik,
              path + "/powtorka/powtorka_puszki/" + plik)
