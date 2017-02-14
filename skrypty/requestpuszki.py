import os
import subprocess
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("slur")
args = parser.parse_args()

path1 = "/srv/ra/audycje/" + args.slur + "/puszka/"
req = []
lista = os.listdir(path1)
lista.sort()
if lista:
    for plik in lista:
        subprocess.call(["/home/liquidsoap/requestpush.sh",
                         args.slur, path1 + plik])
        with open("/home/liquidsoap/request_"
                  + args.slur + ".log", "r") as f:
            req.append(f.readline())

with open("/home/liquidsoap/queue_"+args.slur, "w") as f:
        f.writelines(req)
