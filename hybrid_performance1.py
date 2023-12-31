# -*- coding: utf-8 -*-
"""hybrid_performance1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mkWxppQyLRdx6pd7JJ_LYswPUvFWNpDT

# Libraries
"""

# importing the libraries
import tensorflow as tf
import tensorflow_datasets as tfds
tfds.disable_progress_bar()
from IPython.display import clear_output
import matplotlib.pyplot as plt
import os
import cv2
import timeit
import numpy as np
import pandas as pd
from PIL import Image
from tensorflow import keras
import tensorflow as tf
from keras import Model
import random
import cv2
import warnings
warnings.filterwarnings('ignore')
import skimage
from skimage import io
from glob import glob
import matplotlib.pyplot as plt
from keras.metrics import MeanIoU
from keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD,Adam
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import load_img ,img_to_array
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, roc_auc_score, classification_report
from tensorflow.keras.layers import MaxPooling2D,BatchNormalization,Conv2D,Dense,Activation,Conv2DTranspose,Input
from tensorflow.keras.layers import Flatten,Dropout,SpatialDropout2D,AveragePooling2D,GlobalAveragePooling2D,Concatenate
from keras.models import Model
from keras.layers import Layer
from keras.layers import Conv2D
from keras.layers import Dropout
from keras.layers import UpSampling2D
from keras.layers import concatenate
from keras.layers import Add
from keras.layers import Multiply
from keras.layers import Input
from keras.layers import MaxPool2D
from keras.layers import BatchNormalization

"""# Read dataset"""

data = pd.read_csv('E:\\UP_work_tasks\\brain-tumor\\DATASET1\\kaggle_3m\\data.csv')
data.info()

data.head(10)

data_map = []
for sub_dir_path in glob("E:\\UP_work_tasks\\brain-tumor\\DATASET1\\kaggle_3m\\"+"*"):
    try:
        if os.path.isdir(sub_dir_path):
            dir_name = sub_dir_path.split('/')[-1]
            for filename in os.listdir(sub_dir_path):
                image_path = sub_dir_path + '/' + filename
                data_map.extend([dir_name, image_path])
    except Exception as e:
        print(e)

data = pd.DataFrame({"patient_id" : data_map[::2],
                   "path" : data_map[1::2]})

data_imgs = data[~data['path'].str.contains("mask")]
data_masks = data[data['path'].str.contains("mask")]

# File path line length images for later sorting
BASE_LEN = 89
END_IMG_LEN = 4
END_MASK_LEN = 9
# Data sorting
imgs = sorted(data_imgs["path"].values, key=lambda x : int(x[BASE_LEN:-END_IMG_LEN]))
masks = sorted(data_masks["path"].values, key=lambda x : int(x[BASE_LEN:-END_MASK_LEN]))

# Sorting check
idx = random.randint(0, len(imgs)-1)
print("Path to the Image:", imgs[idx], "\nPath to the Mask:", masks[idx])

# Final dataframe
brain_data = pd.DataFrame({"patient_id": data_imgs.patient_id.values,
                             "image_path": imgs,
                             "mask_path": masks
                            })

def pos_neg_diagnosis(mask_path):
    value = np.max(cv2.imread(mask_path))
    if value > 0 :
        return 1
    else:
        return 0

brain_data['mask'] = brain_data['mask_path'].apply(lambda x: pos_neg_diagnosis(x))

brain_data.head()

brain_data['mask'].value_counts().values

brain_data['mask'].value_counts()

mask_imgs_idx = []
for i in range(len(brain_data)):
    if cv2.imread(brain_data.mask_path[i]).max() > 0:
        mask_imgs_idx.append(i)

# Data Visualization

count = 0
i = 0
fig,axs = plt.subplots(3,3, figsize=(20,50))
for i in mask_imgs_idx:
#     if (mask==1):
    img = io.imread(brain_data.image_path[i])
    axs[count][0].title.set_text("Brain MRI")
    axs[count][0].imshow(img)

    mask = io.imread(brain_data.mask_path[i])
    axs[count][1].title.set_text("Mask")
    axs[count][1].imshow(mask, cmap='gray')

    img[mask==255] = (0,255,150)  # change pixel color at the position of mask
    axs[count][2].title.set_text("MRI with Mask")
    axs[count][2].imshow(img)
    count +=1
    i += 1
    if (count==3):
        break
fig.tight_layout()

masks=brain_data['mask_path']
images=brain_data['image_path']


maskssdata=[]
for i in masks:
    img=cv2.imread(i)
    img = cv2.resize(img,(128,128))
    maskssdata.append(img)

maskssdata=np.array(maskssdata)
print(maskssdata.shape)

imagesdata=[]
for i in range(len(maskssdata)):
    img=cv2.imread(brain_data.image_path[i])
    img = cv2.resize(img,(128,128))
    imagesdata.append(img)

def convertToOneChannel(img):
   im=np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
   i=cv2.resize(im, (128, 128))
   return i

maskssdata=[]
for i in masks:
    img=cv2.imread(i)
    img = cv2.resize(img,(128,128))
    maskssdata.append(img)

maskssdata=np.array(maskssdata)
print(maskssdata.shape)

imagesdata=[]
for i in range(len(maskssdata)):
    img=cv2.imread(brain_data.image_path[i])
    img = cv2.resize(img,(128,128))
    imagesdata.append(img)

y=[]
for i in maskssdata:
    y.append(convertToOneChannel(i))
x=[]
for i in imagesdata:
    x.append(convertToOneChannel(i))
y=np.array(y)
x=np.array(x)
print(y.shape)
print(x.shape)

def convertToThreeChannel(img):
       b_np= np.array(img)
       g_np= np.array(img)
       r_np= np.array(img)
       final_img = np.dstack([b_np, g_np, r_np]).astype(np.uint8)
       return np.array(final_img)

"""# Load Model"""

path='C:\\Users\\radwa\\OneDrive\\Desktop\\performances\\hyprid\\unet.h5'
# load model from file
unet = tf.keras.models.load_model(path)
print(unet)

path='C:\\Users\\radwa\\OneDrive\\Desktop\\performances\\hyprid\\segmented.h5'
# load model from file
segmented = tf.keras.models.load_model(path)
print(segmented)

"""# Test model"""

test=[]
test.append(x[3000])
test=np.array(test)
pred=unet.predict(test)
print(pred.shape)
predimg=convertToThreeChannel(pred[0])
plt.figure
plt.subplot(1,3,1)
plt.imshow(imagesdata[3000])
plt.title("original image")
plt.subplot(1,3,2)
plt.imshow(maskssdata[3000])
plt.title("masked image")
plt.subplot(1,3,3)
plt.imshow(predimg)
plt.title("Predicted  masked")
plt.show()
print(predimg.shape)

"""# train_test_split"""

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 1)

np.array(y_test).shape

np.array(X_test).shape

"""# performance"""

def predict_label(X_test, y_test,model):
  test=[]
  test.extend(X_test)
  test=np.array(test)
  print(test.shape)
  pred=model.predict(test)
  print(pred.shape)
  return(pred)
predicted=predict_label(X_test,y_test,unet)
print(y_test.shape)

predicted[0].min()

predicted2=predict_label(predicted,y_test,segmented)
print(y_test.shape)

predicted2[0].max()



"""# enhance results"""

for i in predicted2:
  i[i <= 0] = 0
for i in predicted2:
  i[i < 0.5] = 0
for i in predicted2:
  i[i >= 0.5] = 255

for i in y_test:
  i[i <= 0] = 0
for i in y_test:
  i[i <= 127] = 0
for i in y_test:
  i[i >= 127] = 255

predicted2=predicted2/255
y_test=y_test/255

predicted2.max()



import numpy as np
predictions_flat = predicted2.flatten()
y_flat = y_test.flatten()
print(np.array(y_flat).shape)

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
print('Train report', classification_report(y_flat, predictions_flat))
print('Train conf matrix', confusion_matrix(y_flat, predictions_flat))

[[tn, fp], [fn, tp]]= confusion_matrix(y_flat, predictions_flat)



def performance(tn,fp,fn,tp):
  dsc = 2*(tp) /(2*(tp) + fp + fn)
  print('Dice Similarity Coefficient /F1-score', dsc)
  iou=fp/(tp+fp+fn)
  print('Intersection-Over-Union ',iou)
  sens=tp/(tp+fn)
  print('sensiSensitivitytivity ',sens)
  spec=tn/(tn+fp)
  print('Specificity ',spec)
  Precision=tp/(tp+fp)
  print('Precision ',Precision)
  a=(tp+tn)/(tp+tn+fp+fn)
  print('accuracy', a)
  Balanced_Accuracy =(sens+spec) /2
  print('Balanced_Accuracy ',Balanced_Accuracy)
  AUC=(1- 0.5*((fp/(fp+tn))+(fn/(fn+tp))))
  print('area under curve ',AUC)
  vs=1-((np.absolute(fn-fp))/((2*tp)+fp+fn))
  print('Volumetric Similarity ',vs)
  return dsc,iou,sens,spec,Precision,a,Balanced_Accuracy,AUC,vs

from sklearn.metrics import cohen_kappa_score
cohen= cohen_kappa_score(y_flat, predictions_flat)
print('cohen_kappa_score  ',cohen)
dsc1,iou1,sens1,spec1,Precision1,a1,Balanced_Accuracy1,AUC1,vs1=performance(tn,fp,fn,tp)

result_hybrid=cohen,dsc1,iou1,sens1,spec1,Precision1,a1,Balanced_Accuracy1,AUC1,vs1

# Commented out IPython magic to ensure Python compatibility.
# %store result_hybrid

print(result_hybrid)



layers_hybrid=len(segmented.layers)+ len(unet.layers)
print(layers_hybrid)

from keras.utils.layer_utils import count_params
trainable_count = count_params(segmented.trainable_weights)
trainable_count1 = count_params(unet.trainable_weights)
sum_param=trainable_count+trainable_count1
print(sum_param)

# Commented out IPython magic to ensure Python compatibility.
# %store layers_hybrid
# %store sum_param

