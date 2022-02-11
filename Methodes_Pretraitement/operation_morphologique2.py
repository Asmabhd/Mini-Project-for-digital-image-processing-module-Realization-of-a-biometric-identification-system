##########  marche #############################################
import numpy as np
import cv2 as cv
import math


def calculate_template_space(temp_side_length):
        return int(temp_side_length/2)


def median_filter(image, template_side_length):
    new_image = np.zeros(image.shape, image.dtype)
    template_space = calculate_template_space(template_side_length)
    template = []
    half_template = int((template_side_length-1)/2)

    for x in range(template_space, new_image.shape[1] - template_space):
        a = x + half_template
        for y in range(template_space, new_image.shape[0] - template_space):
            b = y + half_template
            for c in range(0, template_side_length):
                for d in range(0, template_side_length):
                    template.append(image[b - d, a - c])
            template.sort()
            new_image[y, x] = template[int((int(math.pow(template_side_length, 2)) - 1) / 2)]
            template = []
    return new_image

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

if __name__ == "__main__":
    # Erosion

    img = cv.imread("001_1_1.bmp", cv.IMREAD_GRAYSCALE)
    filter_size = 9
    temp = np.zeros(img.shape, img.dtype)
    new_img = erosion(img, filter_size, temp)
    cv.imwrite("cells_eroded_" + str(filter_size) + "_.png", new_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Dilation
    img = cv.imread("001_1_1.bmp", cv.IMREAD_GRAYSCALE)
    filter_size = 9
    temp = np.zeros(img.shape, img.dtype)
    new_img = dilation(img, filter_size, temp)
    cv.imwrite("cells_dilated_" + str(filter_size) + "_.png", new_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Opening
    img = cv.imread("001_1_1.bmp",cv.IMREAD_GRAYSCALE)
    filter_size = 9
    temp = np.zeros(img.shape, img.dtype)
    new_img = open_op(img, filter_size, temp)
    cv.imwrite("cells_opened_" + str(filter_size) + "_.png", new_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Closing
    img = cv.imread("001_1_1.bmp",cv.IMREAD_GRAYSCALE)
    filter_size = 9
    temp = np.zeros(img.shape, img.dtype)
    new_img = close_op(img, filter_size, temp)
    cv.imwrite("cells_closed_" + str(filter_size) + "_.png", new_img)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
    img = cv.imread("001_1_1.bmp",cv.IMREAD_GRAYSCALE)
    filter_size = 9
    temp = np.zeros(img.shape, img.dtype)
    new_img = lissage(img, filter_size, temp)
    cv.imwrite("lissage_morphologique_" + str(filter_size) + "_.png", new_img)
    cv.waitKey(0)
