import cv2 as cv
import matplotlib.pyplot as plt
import mysql.connector 
import keyword
import re
from PIL import Image
import numpy as np
import sqlite3
import pandas as pd
from pandas import DataFrame
f=[]
f2=[]
#connection a la base de données "iris_base"
conn = sqlite3.connect('Iris_Base_Images.db')
c = conn.cursor()
c.execute('''CREATE TABLE iris
             ([id] INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,[image] BLOB NOT NULL, [keypoints] TEXT, [descriptors] TEXT)''')
#créer sift
sift = cv.SIFT_create()
#ouvrirfichier data2 qui contient les noms de toutes les images
fil=open('data2.txt', 'r')
regex = re.compile(r'[\n\r\t]')
#boucle pour parcourir toutes les lignes de fil et les mettre dans une liste
for j in fil:
   f.append(j)
for s in f:
    s = regex.sub("", s)
    f2.append(s)
#parocurir la liste f2 afin de récuperer
for g in f2:
    a='C:/Users/KENZA/Desktop/baseiris/'+g
    img1 = cv.imread(a,cv.IMREAD_GRAYSCALE)
    #utiliser le detecteur sift pour récuperer keypoints et descriptors
    kp1, des1 = sift.detectAndCompute(img1,None)
    d=des1.tolist()
    d1=str(d)
    k=cv.KeyPoint_convert(kp1)
    k1=k.tolist()
    k2=str(k1)
    #insérer les resultat de détecteur sift dans la table "iris" de la BDD
    c.execute("""INSERT INTO iris(image, keypoints , descriptors) VALUES(?, ?, ?)""",(g,k2,d1) )
    
conn.commit()
conn.close()