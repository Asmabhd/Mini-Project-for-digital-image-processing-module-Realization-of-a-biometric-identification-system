from PIL import Image
import numpy as np
import os
import re

t=open('data2.txt', 'r')
k=1
v=0 
fil=[]
for o in t:
    fil.append(o)

   
while  v < len(fil):
    r='Person_'+str(k)
    os.mkdir(r)
    k=k+1
    regex = re.compile(r'[\n\r\t]')
    x=1
    f=[]
    f2=[]
    z=str(fil[v])
    a=z[0]
    b=z[1]
    c=z[2]
    y=a+b+c
    for j in fil:
        if y in j:
            f.append(j)
    
    for s in f:
        s = regex.sub("", s)
        f2.append(s)
    
    for g in f2:
        img=Image.open('C:/Users/KENZA/Desktop/Allouche_Kenza_Oubara_Mouna_Bouhadadou_Asma/'+g)
        
        img.save(r+'/'+g)    
    x=x+1
    v=v+len(f2)
    
    

    


   

    
    
    
    
    
    
