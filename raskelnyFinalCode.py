# -*- coding: utf-8 -*-
"""Raskelny.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qDTv2bpEzu1Ttt9sP-ZP3xUgM3a4IMG5
"""

# Commented out IPython magic to ensure Python compatibility.
from keras.models import Sequential
from keras.layers import Conv2D, Activation,Dropout
from keras.models import Model,load_model, save_model
from tensorflow.keras.layers import BatchNormalization
from keras.layers.pooling import MaxPooling2D
from keras.layers.core import Flatten, Dense
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import tensorflow.python.keras.engine
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.datasets import load_files
import itertools
import numpy as np
import pandas as pd
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
import itertools
# %matplotlib inline
from tensorflow import lite
from tensorflow.keras import models

Train_path   =  'DATASETS/TRAIN'
Test_path    = 'DATASETS/TEST'

def load_dataset(path):
    data = load_files(path)
    files = np.array(data['filenames'])
    targets = np.array(data['target'])
    target_labels = np.array(data['target_names']) 
    return files,targets,target_labels
    
x_train, y_train,target_labels = load_dataset(Train_path)
x_test, y_test,_ = load_dataset(Test_path)

print('Training set size : ' , x_train.shape[0])
print('Testing set size : ', x_test.shape[0])

x_train,x_validate,y_train,y_validate = train_test_split(x_train, y_train, test_size = 0.2, random_state = 1)



print(f"x_train shape: {str(x_train.shape)}")
print(f"x_train shape: {str(y_train.shape)}")
print(f"x_validate shape: {str(x_validate.shape)}")
print(f"y_validate shape: {str(y_validate.shape)}")
print(f"x_test shape: {str(x_test.shape)}")
print(f"y_test shape: {str(y_test.shape)}")

def convert_image_to_array(files):
    width, height, channels = 64, 64, 3
    images_as_array = np.empty((files.shape[0], width, height, channels), dtype=np.uint8) #define train and test data shape
    for idx,file in enumerate(files):
        img = cv2.imread(file) 
        res = cv2.resize(img, dsize=(width, height), interpolation=cv2.INTER_CUBIC) #As images have different size, resizing all images to have same shape of image array
        images_as_array[idx] = res
    return images_as_array

x_train = np.array(convert_image_to_array(x_train))
print('Training set shape : ',x_train.shape)

x_valid = np.array(convert_image_to_array(x_validate))
print('Validation set shape : ',x_valid.shape)

x_test = np.array(convert_image_to_array(x_test))
print('Test set shape : ',x_test.shape)

x_train = x_train.astype('float32')/255
x_valid = x_valid.astype('float32')/255
x_test = x_test.astype('float32')/255
y_train = y_train.reshape(y_train.shape[0],1)
y_test = y_test.reshape(y_test.shape[0],1)
y_validate = y_validate.reshape(y_validate.shape[0],1)

plt.figure(figsize=(20,20))
classes = ['W','R']
for i in range(1,26):
    index = np.random.randint(x_train.shape[0])
    plt.subplot(5, 5, i)
    plt.imshow(np.squeeze(x_train[index]), cmap='cool')
    plt.title(classes[int(y_train[index])])
    plt.tight_layout()
plt.show()

from glob import glob 

className = glob(Train_path + '/*' )
numberOfClass = len(className)
print("Number Of Class: ",numberOfClass)

datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        zoom_range = 0.1, # Randomly zoom image 
        width_shift_range=0.2,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.2,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=False,  # randomly flip images
        vertical_flip=False)  # randomly flip images
datagen.fit(x_train)

NUM_CLASSES = 2
INPUT_SHAPE=x_train.shape[1:]

from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import regularizers
model = Sequential()
weight_decay = 1e-4
model.add(Conv2D(32, (3,3),
kernel_regularizer=regularizers.l2(weight_decay),kernel_initializer='he_uniform',padding='same', input_shape=INPUT_SHAPE))
model.add(Activation('elu'))
model.add(Conv2D(32, (3,3),kernel_initializer='he_uniform',padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
model.add(Activation('elu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.2))

model.add(Conv2D(64, (3,3),kernel_initializer='he_uniform',padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
model.add(Activation('elu'))
model.add(Conv2D(64, (3,3),kernel_initializer='he_uniform',padding='same',kernel_regularizer=regularizers.l2(weight_decay)))
model.add(Activation('elu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.3))

model.add(Conv2D(128, (3,3),kernel_initializer='he_uniform',padding='same',kernel_regularizer=regularizers.l2(weight_decay)))
model.add(Activation('elu'))
model.add(Conv2D(128, (3,3),kernel_initializer='he_uniform',padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
model.add(Activation('elu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.4))

model.add(Flatten())
#model.add(Dense(128, activation='relu',kernel_initializer='he_uniform'))
#model.add(BatchNormalization())
#model.add(Dropout(0.5))
model.add(Dense(NUM_CLASSES,activation='softmax'))

model.compile(loss = "binary_crossentropy",
              optimizer = "adam",
              metrics = ["accuracy"])
batch_size = 256

train_datagen = ImageDataGenerator(rescale= 1./255)
test_datagen = ImageDataGenerator(rescale= 1./255)

train_generator = train_datagen.flow_from_directory(
        Train_path, 
        target_size= (64,64),
        batch_size = batch_size,
        color_mode= "rgb",
        class_mode= "categorical")

test_generator = test_datagen.flow_from_directory(
        Test_path, 
        target_size= (64,64),
        batch_size = batch_size,
        color_mode= "rgb",
        class_mode= "categorical")

hist = model.fit_generator(
        generator = train_generator,
        epochs=10,
        validation_data = test_generator)

plt.figure(figsize=[10,6])
plt.plot(hist.history["accuracy"], label = "Train acc")
plt.plot(hist.history["val_accuracy"], label = "Validation acc")
plt.legend()
plt.show()

plt.figure(figsize=(10,6))
plt.plot(hist.history['loss'], label = "Train loss")
plt.plot(hist.history['val_loss'], label = "Validation loss")
plt.legend()
plt.show()

test_x, test_y = test_generator.__getitem__(1)

labels = (test_generator.class_indices)
labels = {v: k for k,v in labels.items()}

preds = model.predict(test_x)

plt.figure(figsize=(16, 16))
for i in range(15):
    plt.subplot(4, 4, i+1)
    plt.title(
        f'pred:{labels[np.argmax(preds[i])]} / truth:{labels[np.argmax(test_y[i])]}'
    )

    plt.imshow(test_x[i])

# Save the model as a file
model_filename = 'wake_word_stop_model.h5'

save_model(model, model_filename)

# Display model
model.summary()

keras_model_filename = 'wake_word_stop_model.h5'
tflite_filename = 'wake_word_stop_lite.tflite'

# Convert model to TF Lite model
model = models.load_model(keras_model_filename)
converter = lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open(tflite_filename, 'wb').write(tflite_model)

converter =tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
tflite_model = converter.convert()
open(f'{tflite_filename}.tflite', 'wb').write(tflite_model)

