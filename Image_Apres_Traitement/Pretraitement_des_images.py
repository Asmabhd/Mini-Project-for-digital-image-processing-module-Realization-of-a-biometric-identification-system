import math
import numpy as np
from PIL import Image, ImageStat

from IPython.display import display, Math, Latex
import matplotlib.pyplot as plt
import cv2 as cv

import numpy
import os
import re
#fonction converger la matrice de k points a une liste de k points
def converged(centroids, old_centroids):
	if len(old_centroids) == 0:
		return False
	if len(centroids) <= 5:
		a = 1
	elif len(centroids) <= 10:
		a = 2
	else:
		a = 4
	for i in range(0, len(centroids)):
		cent = centroids[i]
		old_cent = old_centroids[i]

		if ((int(old_cent[0]) - a) <= cent[0] <= (int(old_cent[0]) + a)) and ((int(old_cent[1]) - a) <= cent[1] <= (int(old_cent[1]) + a)) and ((int(old_cent[2]) - a) <= cent[2] <= (int(old_cent[2]) + a)):
			continue
		else:
			return False
	return True
#fonction pour recuperer le minimum entre pixel et centroids
def getMin(pixel, centroids):
	minDist = 9999
	minIndex = 0
	for i in range(0, len(centroids)):
		d = numpy.sqrt(int((centroids[i][0] - pixel[0]))**2 + int((centroids[i][1] - pixel[1]))**2 + int((centroids[i][2] - pixel[2]))**2)
		if d < minDist:
			minDist = d
			minIndex = i
	return minIndex
#fonction pour calculer le clusters
def assignPixels(centroids):
	clusters = {}
	for x in range(0, img_width):
		for y in range(0, img_height):
			p = px[x, y]
			minIndex = getMin(px[x, y], centroids)

			try:
				clusters[minIndex].append(p)
			except KeyError:
				clusters[minIndex] = [p]
	return clusters
# fonction pour ajuster le centroids
def adjustCentroids(centroids, clusters):
	new_centroids = []
	keys = sorted(clusters.keys())
	for k in keys:
		n = numpy.mean(clusters[k], axis=0)
		new = (int(n[0]), int(n[1]), int(n[2]))
		print(str(k) + ": " + str(new))
		new_centroids.append(new)
	return new_centroids
# fonction pour appliquer le Kmeans
def startKmeans(someK):
	centroids =[(27, 27, 27), (170, 170, 170), (142, 142, 142), (0, 0, 0), (73, 73, 73), (123, 123, 123), (0, 0, 0)]
	old_centroids = []
	rgb_range = ImageStat.Stat(im).extrema
	i = 1
	while not converged(centroids, old_centroids) and i <= 20:
		print("Iteration #" + str(i))
		i += 1
		old_centroids = centroids 								#Make the current centroids into the old centroids
		clusters = assignPixels(centroids) 						#Assign each pixel in the image to their respective centroids
		centroids = adjustCentroids(old_centroids, clusters) 	#Adjust the centroids to the center of their assigned pixels
	return centroids
# fonction qui utilise l'image originale et qui appelle les autres fonction
def drawWindow(result):
	img = Image.new('RGB', (img_width, img_height), "white")
	p = img.load()
	for x in range(img.size[0]):
		for y in range(img.size[1]):
			RGB_value = result[getMin(px[x, y], result)]
			p[x, y] = RGB_value
	return img

def calculate_template_space(temp_side_length):
        return int(temp_side_length/2)
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

#fonction pour effectuer l'opération de l'erosion sur une image 
def erosion(image, template_side_length, template):
    #crée une nouvelle image avec les meme dimension de l'ancien image
    new_image = np.zeros(image.shape, image.dtype)
    #template_side_length = le size de filtre 
    template_space = calculate_template_space(template_side_length)
    #calculer la moitier de size de filtre
    half_template = int((template_side_length - 1) / 2)
    #boucle pour appliquer le principe d'erosion sur chaque pixel
    #parcourir les lignes et les colonnes de l'image
    for x in range(template_space, new_image.shape[1] - template_space):
        for y in range(template_space, new_image.shape[0] - template_space):
            minimum = 256
            #parcourir les lignes et les colonnes de filtre
            for c in range(0, template_side_length):
                for d in range(0, template_side_length):
                    a = x - half_template - 1 + c
                    b = y - half_template - 1 + d
                    sub = image[b, a] - template[d, c]
                    if sub < minimum:
                        if sub > 0:
                            minimum = sub
            new_image[y, x] = int(minimum)
    return new_image

#fonction pour effectuer l'opération de dilatation sur une image 
def dilation(image, template_side_length, template):
    #crée une nouvelle image avec les meme dimension de l'ancien image
    new_image = np.zeros(image.shape, image.dtype)
    #template_side_length = le size de filtre 
    template_space = calculate_template_space(template_side_length)
    #calculer la moitier de size de filtre
    half_template = int((template_side_length - 1) / 2)
    #boucle pour appliquer le principe de dilatation sur chaque pixel
    #parcourir les lignes et les colonnes de l'image
    for x in range(template_space, new_image.shape[1] - template_space):
        for y in range(template_space, new_image.shape[0] - template_space):
            maximum = 0
            #parcourir les lignes et les colonnes de filtre
            for c in range(0, template_side_length):
                for d in range(0, template_side_length):
                    a = x - half_template - 1 + c
                    b = y - half_template - 1 + d
                    sub = image[b, a] - template[d, c]
                    if sub > maximum:
                        if sub > 0:
                            maximum = sub
            new_image[y, x] = int(maximum)
    return new_image

#fonction pour effectuer l'opération d'ouverture(open) sur une image 
def open_op(image, template_side_length, template):
    #l'ouverture = dilatation(erosion(image,filtre),filtre)
    #template_side_length=taille de filtre
    new_image = erosion(image, template_side_length, template)
    new_image_2 = dilation(new_image, template_side_length, template)
    return new_image_2

#fonction pour effectuer l'opération de fermeture(close) sur une image 
def close_op(image, template_side_length, template):
    #fermeture = erosion(dilatation(image,filtre),filtre)
    #template_side_length=taille de filtre
    new_image = dilation(image, template_side_length, template)
    new_image_2 = erosion(new_image, template_side_length, template)
    return new_image_2

#fonction pour effectuer l'opération de lissage morphologique sur l'image 
def lissage(image, template_side_length, template):
    #lissage morphologique=fermeture(ouverture(image,filtre),filtre)
    #template_side_length=taille de filtre
    new_image1=open_op(image, template_side_length, template)
    new_image2=close_op(new_image1, template_side_length, template)
    return new_image2
def filtreGaussien(P):
    print("debut filtr lis gos")
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
t=open('data2.txt', 'r')
k=1
fil=[]
for o in t:
    fil.append(o)
k=1
v=54
while  v < len(fil):
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
        img=Image.open('C:/Users/pc/.spyder-py3/tin/Casia v1/Casia v1/'+g)
        print(g)
        # convert image into a numpy array
        img = np.asarray(img)
        X2 = np.array(img)
        h = filtreGaussien(5)             
        Y = convolution2D(X2,h,False)
        imag = Image.fromarray(Y)
        img = np.array(imag)
        
        # put pixels in a 1D array by flattening out img array
        flat = img.flatten()
        # formula for creating the histogram
        #display(Math(r'P_x(j) = \sum_{i=0}^{j} P_x(i)'))
        # create our own histogram function
        def get_histogram(image, bins):
            # array with size of bins, set to zeros
            histogram = np.zeros(bins)
            # loop through pixels and sum up counts of pixels
            for pixel in image:
                histogram[pixel] += 1            
            # return our final result
            return histogram        
        hist = get_histogram(flat, 256)
        plt.plot(hist)
        # create our cumulative sum function
        def cumsum(a):
            a = iter(a)
            b = [next(a)]
            for i in a:
                b.append(b[-1] + i)
            return np.array(b)
        # execute the fn
        cs = cumsum(hist)
        #plt.plot(cs)
        # display the result
        # formula to calculate cumulation sum
        #display(Math(r's_k = \sum_{j=0}^{k} {\frac{n_j}{N}}'))
        # re-normalize cumsum values to be between 0-255
        # numerator & denomenator
        nj = (cs - cs.min()) * 255
        N = cs.max() - cs.min()
        n=abs(cs*255)
        # re-normalize the cdf
        cs = nj / N
        # cast it back to uint8 since we can't use floating point values in images
        cs = cs.astype('uint8')
        # get the value from cumulative sum for every index in flat, and set that as img_new
        img_new = cs[flat]
        # put array back into original shape since we flattened it
        img_new = np.reshape(img_new, img.shape)
        filter_size = 9
        temp = np.zeros(img_new.shape, img.dtype)
        img_new = Image.fromarray(img_new)
        k_input = int(9)
        
        im=img_new.convert('RGB')
        img_width, img_height = im.size
        px = im.load()
        
        result = startKmeans(k_input)
        img_new=drawWindow(result)
        img_new.save('r1.png')
        img_new = cv.imread("r1.png", cv.IMREAD_GRAYSCALE)
        if os.path.exists('r1.png'):
            os.remove('r1.png')
        #img_new = open_op(img_new, filter_size, temp)
        img_new = dilation(img_new, filter_size, temp)
        img_new = erosion(img_new, filter_size, temp)
        #img_new = close_op(img_new, filter_size, temp)
        img_new = lissage(img_new, filter_size, temp)

        cv.imwrite(g,img_new)  
    x=x+1
    v=v+len(f2)