############# marche  #######################################
import math
import numpy as np
from PIL import Image 
#fonction de convolution2D
def convolution2D(X,H,moitie):
    s = X.shape
    py = int((H.shape[0]-1)/2)
    px = int((H.shape[1]-1)/2)
    Y = X.copy()
    if moitie:
        imax = int(s[1]/2)
    else:
        imax = int(s[1]-px)
    for i in range(px,imax):
        for j in range(py,s[0]-py):
            somme = 0.0
            for k in range(-px,px+1):
                for l in range(-py,py+1):
                    somme += X[j+l][i+k]*H[l+py][k+px]
            Y[j][i] = somme
    return Y
# fonction de filtre gaussien qui calcule le filtre
def filtreGaussien(P):
    epsilon = 0.05
    sigma = P*1.0/math.sqrt(-2*math.log(epsilon))
    h = np.zeros((2*P+1,2*P+1))
    som = 0
    for m in range(-P,P+1):
        for n in range(-P,P+1):
            h[m+P][n+P] = math.exp(-(n*n+m*m)/(2*sigma*sigma))
            som += h[m+P][n+P]
    h = h/som
    return h

im = Image.open('001_1_1.bmp') 
img = np.array(im) 
X2 = np.array(img)
h = filtreGaussien(5)             
Y = convolution2D(X2,h,False)
imag = Image.fromarray(Y)
imag.show()

#imshow(Y,cmap=cm.gray)