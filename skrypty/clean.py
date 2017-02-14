import os
import subprocess
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("slur")
args = parser.parse_args()

lista = []
with open("/home/liquidsoap/queue_"+args.slur, "r") as f:
    lista = f.readlines()

for numer in lista:
    subprocess.call(["/home/liquidsoap/requestremove.sh",
                     args.slur, numer.replace('\n', '')])
