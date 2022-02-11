###################### ajustement de contraste################
from IPython.display import display, Math, Latex

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
img = Image.open('001_1_1.bmp')
# convertir une image 
img = np.asarray(img)
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
flat2 = img_new.flatten()
histnew = get_histogram(flat2, 256)
plt.plot(histnew)
# set up side-by-side image display
fig = plt.figure()
fig.set_figheight(15)
fig.set_figwidth(15)
fig.add_subplot(1,2,1)
plt.imshow(img, cmap='gray')
# display the new image
fig.add_subplot(1,2,2)
plt.imshow(img_new, cmap='gray')