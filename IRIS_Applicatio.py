#*******************************les bibliothèques python*************************#
from tkinter import *
from tkinter import filedialog
import os
import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageStat
import cv2
import numpy as np
import numpy
import math
from IPython.display import display, Math, Latex
import matplotlib.pyplot as plt
import cv2 as cv
from tkinter import ttk
import mysql.connector 
import keyword
import re
from io import BytesIO
from tkinter.commondialog import Dialog
from tkinter.ttk import Progressbar
import sqlite3

#**************************les messages d'alertes*********************************#
_all_ = ["showinfo"]
INFO = "info"
ABORTRETRYIGNORE = "abortretryignore"
OK = "ok"
OKCANCEL = "okcancel"
RETRYCANCEL = "retrycancel"
YESNO = "yesno"
YESNOCANCEL = "yesnocancel"
ABORT = "abort"
RETRY = "retry"
IGNORE = "ignore"
OK = "ok"
CANCEL = "cancel"
YES = "yes"
NO = "no"
#fonction pour fermer messagebox
def on_closing():
    #if messagebox.askokcancel("Quit", "voulez vous fermer la fenetre?"):

    app.destroy()
    if os.path.exists('orig.jpg'):
        os.remove('orig.jpg')
    if os.path.exists('kk.jpg'):
        os.remove('kk.jpg')
    if os.path.exists('gaus.jpg'):
        os.remove('gaus.jpg')
            
    if os.path.exists('resultat.bmp'):
        os.remove('resultat.bmp')
    if os.path.exists('r1.png'):
        os.remove('r1.png')
        
class Message(Dialog):
    "A message box"

    command  = "tk_messageBox"
#fonction pour afficher messagebox
def _show(title=None, message=None, _icon=None, _type=None, **options):
    if _icon and "icon" not in options:    options["icon"] = _icon
    if _type and "type" not in options:    options["type"] = _type
    if title:   options["title"] = title
    if message: options["message"] = message
    res = Message(**options).show()
    # In some Tcl installations, yes/no is converted into a boolean.
    if isinstance(res, bool):
        if res:
            return YES
        return NO
    # In others we get a Tcl_Obj.
    return str(res)


def showinfo(title=None, message=None, **options):
    "Show an info message"
    return _show(title, message, INFO, OK, **options)
#***************** fonction pour la mise en crrespondance (Matching)
#fonction pour convertir les points en keypoints 
def convert_pts_to_keypoints(pts, size=1): 
    kps = []
    if pts is not None: 
        if pts.ndim > 2:
            # convert matrix [Nx1x2] of pts into list of keypoints  
            kps = [ cv.KeyPoint(p[0][0], p[0][1], _size=size) for p in pts ]          
        else: 
            # convert matrix [Nx2] of pts into list of keypoints  
            kps = [ cv.KeyPoint(p[0], p[1], _size=size) for p in pts ]                      
    return kps 
#fonction pour verifier dans la base de données
def identifier(image):
    #connection a la base
    try:
        sqliteConnection = sqlite3.connect('Iris_Base_Images.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        #selectionner des informations dans la base
        sqlite_select_query = """SELECT image, keypoints , descriptors FROM iris"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Total rows are:  ", len(records))
        print("Printing each row")
        
        img1 = cv.imread(image,cv.IMREAD_GRAYSCALE)
        sift = cv.SIFT_create()
        
        # trouver le keypoints et descriptors avec SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        
        j=0
        for row in records:
            j=j+1
            print(j)
            #debut de verification avec les informations stocker dans la base de données
            img2=cv.imread(row[0],cv.IMREAD_GRAYSCALE) 
            kp2=convert_pts_to_keypoints(np.array(eval(row[1])), size=1)
            des2=np.float32(eval(row[2])) 
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
            search_params = dict(checks=50)   # or pass empty dictionary
        
            flann = cv.FlannBasedMatcher(index_params,search_params)
            
            matches = flann.knnMatch(des1,des2,k=2)
            
            # appliquer le test de matching
            good = []
            for m,n in matches:
                if m.distance < 0.75*n.distance:
                    good.append([m])
                    a=len(good)
            percent=(a*100)/len(kp2)
            #si le pourcentage de similarité superieur a 70: existe
            p="{} % similaire".format(percent)
            if percent >= 70.00:
                print('Existe')
                z='Exist'
                break
            else:
                #si le pourcentage de similarité superieur a 70: n'existe pas
                z='N\'existe pas'
                print(z)
            print(z)
            print(p)
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    return z,p



def calculate_template_space(temp_side_length):
        return int(temp_side_length/2)
#fonction de convolution2D
def convolution2D(X,H,moitie):
    print("debut de lissage gaussien")
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
    print("fin de lissage gaussien")
    return Y
#fonction pour effectuer l'opération de l'erosion sur une image 
def erosion(image, template_side_length, template):
    print("debut de erosion")
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
    print("fin de erosion")
    return new_image

#fonction pour effectuer l'opération de dilatation sur une image 
def dilation(image, template_side_length, template):
    print("debut dilatation")
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
    print("fin dilatation")
    return new_image

#fonction pour effectuer l'opération d'ouverture(open) sur une image 
def open_op(image, template_side_length, template):
    print("debut ouverture")
    #l'ouverture = dilatation(erosion(image,filtre),filtre)
    #template_side_length=taille de filtre
    new_image = erosion(image, template_side_length, template)
    new_image_2 = dilation(new_image, template_side_length, template)
    print("fin ouverture")
    return new_image_2

#fonction pour effectuer l'opération de fermeture(close) sur une image 
def close_op(image, template_side_length, template):
    print("debut de fermeture")
    #fermeture = erosion(dilatation(image,filtre),filtre)
    #template_side_length=taille de filtre
    new_image = dilation(image, template_side_length, template)
    new_image_2 = erosion(new_image, template_side_length, template)
    print("fin de fermeture")
    return new_image_2

#fonction pour effectuer l'opération de lissage morphologique sur l'image 
def lissage(image, template_side_length, template):
    print("debut de lissage morphologique")
    #lissage morphologique=fermeture(ouverture(image,filtre),filtre)
    #template_side_length=taille de filtre
    new_image1=open_op(image, template_side_length, template)
    new_image2=close_op(new_image1, template_side_length, template)
    print("fin de lissage morphologique")
    return new_image2
# fonction de filtre gaussien qui calcule le filtre
def filtreGaussien(P):
    print("debut de filtre gaussien")
    epsilon = 0.05
    sigma = P*1.0/math.sqrt(-2*math.log(epsilon))
    h = np.zeros((2*P+1,2*P+1))
    som = 0
    for m in range(-P,P+1):
        for n in range(-P,P+1):
            h[m+P][n+P] = math.exp(-(n*n+m*m)/(2*sigma*sigma))
            som += h[m+P][n+P]
    h = h/som
    print("fin de filtre gaussien")
    return h

def get_histogram(image, bins):
    print("debut de amelioration de cotras")
    # array with size of bins, set to zeros
    histogram = np.zeros(bins)
    
    # loop through pixels and sum up counts of pixels
    for pixel in image:
        histogram[pixel] += 1
    
    # return our final result
    return histogram
def cumsum(a):
    a = iter(a)
    b = [next(a)]
    for i in a:
        b.append(b[-1] + i)
    print("fin de amelioration de cotras")
    return np.array(b)


#===================================================================================================#
class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
     

# la premiére page d'interface 
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Systeme biometrique de detection de l'individu par l'IRIS", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Verification ",
                            command=lambda: controller.show_frame("PageOne"),bg='light goldenrod',fg='blue')
        button2 = tk.Button(self, text="Traitement",
                            command=lambda: controller.show_frame("PageTwo"),bg='light goldenrod',fg='blue')
        
        
        button1.place(x=300,y=70,width=150,height=30,anchor='n')
        button2.place(x=500,y=70,width=150,height=30,anchor='n')
        label = tk.Label(self, font=controller.title_font)
        label.pack(side="top", fill="x", pady=50)
        self.can= Canvas (self,width=800,height=600,bg='gray94')
        self.img=ImageTk.PhotoImage(Image.open('nn.ico'))
        self.can.create_image(250,0,anchor=NW,image=self.img)
        self.can.pack()
#************************* la premiere page ****************************
class PageOne(tk.Frame):
    
    def __init__(self, parent, controller):
        global imag
        #fonction pour selectionner et afficher les images
        def showimage():
            
            fln=filedialog.askopenfilename(initialdir=os.getcwd,title="select image",filetypes=(("JPG File","*.jpg"),("PNG file","*.png"),("All files","*.*")))
            img=Image.open(fln)
            imag = img
            
            imag.save('orig.jpg')
            img.thumbnail((200,320))
            
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img)
            lbl.image=img
        def showimage2():
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
            print("info", showinfo("Information", "Le chargement de l'image peut prendre un certain temps, veuillez patienter un peu "))
            #fln=filedialog.askopenfilename(initialdir=os.getcwd,title="select image",filetypes=(("JPG File","*.jpg"),("PNG file","*.png"),("All files","*.*")))
            img2=Image.open('orig.jpg')
            img = np.asarray(img2)
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
            print("debut de segmentation")
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
            print("fin de segmentation")
            #img_new = open_op(img_new, filter_size, temp)
            img_new = dilation(img_new, filter_size, temp)
            img_new = erosion(img_new, filter_size, temp)
            #img_new = close_op(img_new, filter_size, temp)
            img_new = lissage(img_new, filter_size, temp)
            cv.imwrite('resultat.bmp',img_new)
            img1=Image.open('resultat.bmp')
        
            
            img2.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img2=ImageTk.PhotoImage(img2)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img2)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
            
        def matching():
            
            print("info", showinfo("Information", "Le chargement de l'image peut prendre un certain temps, veuillez patienter un peu "))
            img1=Image.open('resultat.bmp')
            #//////////
            
            img2=Image.open('orig.jpg')
        
            img2.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img2=ImageTk.PhotoImage(img2)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img2)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            
            z,p =identifier('resultat.bmp')
            a=z+' '+p
            text.set(a)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
            
            
        tk.Frame.__init__(self, parent)
        self.controller = controller
        frame1=tk.Frame(self)
        frame1.place(x=400,y=0,width=700,height=300,anchor='n')
        label = tk.Label(self, text="Verification ", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        frame=tk.Frame(self,highlightbackground="gray",highlightcolor="gray",highlightthickness=1.5,bd=10)
        frame.place(x=400,y=100,width=700,height=300,anchor='n')
        frame2=tk.Frame(frame,highlightbackground="gray",highlightcolor="gray",bd=10)
        frame2.place(x=150,y=50,width=230,height=200,anchor='n')
        frame3=tk.Frame(frame,highlightbackground="gray",highlightcolor="gray",bd=10)
        frame3.place(x=520,y=50,width=230,height=200,anchor='n')
        frame4=tk.Frame(self,highlightbackground="gray",highlightcolor="gray",highlightthickness=1.5,bd=10)
        frame4.place(x=400,y=370,width=700,height=100,anchor='n')
        can1 = Canvas(frame2,width=280, height=200,  bg='ivory')
        can1.pack(side=TOP, padx=2, pady=2)
        can2 = Canvas(frame3,width=280, height=200,  bg='ivory')
        can2.pack(side=TOP, padx=2, pady=2) 
        button = tk.Button(self, text="retour a la page precedente",
                           command=lambda: controller.show_frame("StartPage"),bg='light goldenrod',fg='black')
        button.place(x=100,y=25,width=150,height=30,anchor='n')
        
        btn1=Button(frame,text='Choisir Image',command=showimage,bg='black',fg='white').place(x=100, anchor='n')
        btn2=Button(frame,text='Traitment Image',command=showimage2,bg='black',fg='white').place(x=520, anchor='n')
        text = tk.StringVar()
        text.set("Resultat")
        label = tk.Label(frame4, textvariable=text,font=("Arial", 15),fg='red')
        label.pack(pady=20)
        match_btn=Button(frame4,text='Matching',command=matching,bg='black',fg='white').place(x=50, anchor='n')

#************************** la deuxieme page *****************************

class PageTwo(tk.Frame):
    

    def __init__(self, parent, controller):
        #afficher les images
        def showimage():
            fln=filedialog.askopenfilename(initialdir=os.getcwd,title="select image",filetypes=(("JPG File","*.jpg"),("PNG file","*.png"),("All files","*.*")))
            img=Image.open(fln)
            imag = img
            
            imag.save('orig.jpg')
            
            img.thumbnail((200,320))
            
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            
           
            lbl=tk.Label(self)
            lbl.configure(image=img)
            lbl.image=img
        #appliquer le filtre gaussien sur l'image
        def gauss_showimage():
            print("info", showinfo("Information", "Le chargement de l'image peut prendre un certain temps, veuillez patienter un peu "))
            img=Image.open('orig.jpg')
            

            # convert image into a numpy array
            img1 = np.asarray(img)
            X2 = np.array(img)
            h = filtreGaussien(5)             
            Y = convolution2D(X2,h,False)
            img1 = Image.fromarray(Y)
            img1.save('gaus.jpg')
            
            img.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
        #appliquer l'ajustement de contraste sur l'image
        def Ajust_showimage():
            
            img=Image.open('orig.jpg')
            img = np.asarray(img)
            flat = img.flatten()
            hist = get_histogram(flat, 256)
            cs = cumsum(hist)            
            nj = (cs - cs.min()) * 255
            N = cs.max() - cs.min()
            n=abs(cs*255)
            cs = nj / N
            cs = cs.astype('uint8')
            img_new = cs[flat]
            img_new = np.reshape(img_new, img.shape)
            flat2 = img_new.flatten()
            histnew = get_histogram(flat2, 256)
            cv2.imwrite('kk.jpg', img_new)
            img1 = Image.open('kk.jpg')
            img = Image.open('orig.jpg')
            img.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
        #appliquer la segmentation sur l'image
        def Seg_showimage():
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
                print("info", showinfo("Information", "Le chargement de l'image peut prendre un certain temps, veuillez patienter un peu "))
                img = Image.open('orig.jpg')
                k_input = int(9)
                im = Image.open('orig.jpg')
                
                im=im.convert('RGB')
                img_width, img_height = im.size
                px = im.load()
                result = startKmeans(k_input)
                h=drawWindow(result)
                h.save('r1.png')
                img1=Image.open('r1.png')
                img1=drawWindow(result)
                img.thumbnail((200,320))
                img1.thumbnail((200,320))
                can1.pack(side=LEFT)
                img=ImageTk.PhotoImage(img)
                img1=ImageTk.PhotoImage(img1)
                can1.create_image(0, 0, anchor=NW, image=img)
                can1.pack(side=TOP, padx=5, pady=5)
                can2.create_image(1, 1, anchor=NW, image=img1)
                can2.pack(side=BOTTOM, padx=5, pady=5)
                lbl=tk.Label(self)
                lbl.configure(image=img1)
                lbl.image=img1
        #apliquer le dilatation sur l'image
        def Delataion_showimage():
            img = Image.open('orig.jpg')
            filter_size = 9
            img1 = np.asarray(img)
            temp = np.zeros(img1.shape, img1.dtype)
            img1 = dilation(img1, filter_size, temp)
            img1 = Image.fromarray(img1)
            img.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
            
        #apliquer l'érosion sur l'image
        def Erosion_showimage():
            img = Image.open('orig.jpg')
            filter_size = 9
            img1 = np.asarray(img)
            temp = np.zeros(img1.shape, img1.dtype)
            img1 = erosion(img1, filter_size, temp)
            img1 = Image.fromarray(img1)
            img.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
        #appliquer le lissage morphologique sur l'image
        def Lissage_morpho_showimage():
            print("info", showinfo("Information", "Le chargement de l'image peut prendre un certain temps, veuillez patienter un peu "))
            img = Image.open('orig.jpg')
            filter_size = 9
            img1 = np.asarray(img)
            temp = np.zeros(img1.shape, img1.dtype)
            img1 = lissage(img1, filter_size, temp)
            img1 = Image.fromarray(img1)
            img.thumbnail((200,320))
            img1.thumbnail((200,320))
            can1.pack(side=LEFT)
            img=ImageTk.PhotoImage(img)
            img1=ImageTk.PhotoImage(img1)
            can1.create_image(0, 0, anchor=NW, image=img)
            can1.pack(side=TOP, padx=5, pady=5)
            can2.create_image(1, 1, anchor=NW, image=img1)
            can2.pack(side=BOTTOM, padx=5, pady=5)
            lbl=tk.Label(self)
            lbl.configure(image=img1)
            lbl.image=img1
            
        tk.Frame.__init__(self, parent)
        self.controller = controller
        frame1=tk.Frame(self)
        frame1.place(x=400,y=0,width=700,height=300,anchor='n')
        label = tk.Label(self, text="Traitement", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        frame=tk.Frame(self,highlightbackground="gray",highlightcolor="gray",highlightthickness=1.5,bd=10)
        frame.place(x=400,y=100,width=700,height=300,anchor='n')
        frame2=tk.Frame(frame,highlightbackground="gray",highlightcolor="gray",bd=10)
        frame2.place(x=150,y=50,width=230,height=200,anchor='n')
        frame3=tk.Frame(frame,highlightbackground="gray",highlightcolor="gray",bd=10)
        frame3.place(x=520,y=50,width=230,height=200,anchor='n')
        frame4=tk.Frame(self,highlightbackground="gray",highlightcolor="gray",highlightthickness=1.5,bd=10)
        frame4.place(x=400,y=370,width=700,height=100,anchor='n')
        can1 = Canvas(frame2,width=280, height=200, bg='ivory')
        can1.pack(side=TOP, padx=2, pady=2)
        can2 = Canvas(frame3,width=280, height=200, bg='ivory')
        can2.pack(side=TOP, padx=2, pady=2) 
        button = tk.Button(self, text="retour a la page precedente",
                           command=lambda: controller.show_frame("StartPage"),bg='light goldenrod',fg='black')
        button.place(x=100,y=25,width=150,height=30,anchor='n')
        
        btn1=Button(frame,text='Choisir Image',command=showimage,bg='black',fg='white').place(x=100, anchor='n')
        lisage_gos_btn=Button(frame4,text='Lissage_Gaussien',command=gauss_showimage,bg='black',fg='white').place(x=50,width=100,height=30, anchor='n')
        cotras_btn=Button(frame4,text='Ajustement',command=Ajust_showimage,bg='black',fg='white').place(x=160,width=100,height=30, anchor='n')
        seg_btn=Button(frame4,text='Segmmentation',command=Seg_showimage,bg='black',fg='white').place(x=270,width=100,height=30, anchor='n')
        delt_btn=Button(frame4,text='Delataion',command=Delataion_showimage,bg='black',fg='white').place(x=380,width=100,height=30, anchor='n')
        eros_btn=Button(frame4,text='Erosion',command=Erosion_showimage,bg='black',fg='white').place(x=490,width=100,height=30, anchor='n')
        lisagemopho_btn=Button(frame4,text='Lissage_morpho',command=Lissage_morpho_showimage,bg='black',fg='white').place(x=600,width=100,height=30, anchor='n')
        


if __name__ == "__main__":
    
    app = SampleApp()
    app.iconphoto(False, tk.PhotoImage(file='a.png'))
    app.title("IRIS")
    app.geometry("800x540")
    
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.resizable(width=0, height=0)
    app.mainloop()
  


    