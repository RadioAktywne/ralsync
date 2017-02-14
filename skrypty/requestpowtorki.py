import os
import subprocess
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("slur")
args = parser.parse_args()

path1 = "/srv/ra/audycje/" + args.slur + "/powtorka/"
path2 = path1 + "powtorka_puszki/"
req = []
lista = os.listdir(path2)
if lista:
    lista.sort()
    for plik in lista:
        subprocess.call(["/home/liquidsoap/requestpush.sh",
                         args.slur, path2 + plik])
        with open("/home/liquidsoap/request_" + args.slur + ".log", "r") as f:
            req.append(f.readline())
else:
    lista = os.listdir(path1)
    lista.sort()
    if lista:
        for plik in lista:
            if pathlib.Path(path1 + plik).is_dir() is False:
                subprocess.call(["/home/liquidsoap/requestpush.sh",
                                 args.slur, path1 + plik])
                with open("/home/liquidsoap/request_" + args.slur
                          + ".log", "r") as f:
                    req.append(f.readline())

with open("/home/liquidsoap/queue_"+args.slur+".log", "w") as f:
    f.writelines(req)
