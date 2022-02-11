import csv
import pandas as pd
from pandas import read_csv
file = open('Casia v1/casia segmentation without.txt', 'r').read()
fichier = open("data.txt", "a")
for iris in file.split('\')'):
    for entry in iris.split('(\''):
        for a in entry.split('function entreiner_casia1_without'):
            for b in a.split('[template111, mask111] = createiristemplate'): 
                for c in b.split('[template112, mask112] = createiristemplate'):
                     for d in c.split('[template113, mask113] = createiristemplate'):
                        for e in d.split('[template121, mask121] = createiristemplate'):
                            for f in e.split('[template122, mask122] = createiristemplate'):
                                for g in f.split('[template123, mask123] = createiristemplate'):
                                    for h in g.split('[template124, mask124] = createiristemplate'):
                                        for i in h.split('[template, mask] = createiristemplate'):
                                            for j in i.split('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  21 --> 40 %%%%%%%%%%%%%%%%%'):
                                                for k in j.split('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  41 --> 60 %%%%%%%%%%%%%%%%%'):
                                                    for l in k.split('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  61 --> 80 %%%%%%%%%%%%%%%%%'):
                                                        for m in l.split('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  81 --> 100 %%%%%%%%%%%%%%%%%'):
                                                            for n in m.split('%%%%%%%%%%%%%%%%%%%  101 --> 108 %%%%%%%%%%%%%%%%'):
                                                                for o in n.split('end'):
                                                                        for p in o.split(';'):
                                                                            fichier.write(p)   
                                                                            
                                                                      
fichier.close()
import fileinput
import sys
for line_number, line in enumerate(fileinput.input('data.txt', inplace=1)):
    if len(line) > 1:
            sys.stdout.write(line)  