# -*- coding: utf-8 -*-
"""Submition2DataTime.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q13yH9miPvqdAKu1ktlnusT76gUfDDow

Mohamad Nafis (Blitar)
> Dataset : "weatherinfoweek" \
> Sumber : Kaggle \
> Link Dataset : https://www.kaggle.com/code/davidbnn92/weather-data
"""

import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense,Bidirectional,Dropout

import pandas as pd

dt = pd.read_csv('weatherinfoweek.csv')
dt

dt.drop(['Id','Province/State','ConfirmedCases', 'Fatalities', 'day_from_jan_first'], axis=1, inplace=True)
dt.head()

dt.isnull().sum()

dt.dropna(subset=['min'],inplace=True)
dt.dropna(subset=['max'],inplace=True)
dt.dropna(subset=['slp'],inplace=True)
dt.dropna(subset=['dewp'],inplace=True)
dt.dropna(subset=['rh'],inplace=True)
dt.dropna(subset=['ah'],inplace=True)
dt.isnull().sum()

df_plot = df
df_plot[df_plot.columns.to_list()].plot(subplots=True, figsize=(15, 9))
plt.show()

dates = dt['Date'].values
temp = dt['temp'].values

dates = np.array(dates)
temp = np.array(temp)

plt.figure(figsize=(20,5))
plt.plot(dates, temp)
plt.title('Temperature average',
          fontsize=20);
plt.ylabel('Temperature')
plt.xlabel('Datetime')

dt.dtypes

x_train, x_valid, y_train, y_valid = train_test_split(temp, dates, train_size=0.8, test_size = 0.2, shuffle = False )

print('Total Data Latih : ',len(x_train))
print('Total Data Validation : ',len(x_valid))

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

tf.keras.backend.set_floatx('float64')

train_set = windowed_dataset(x_train, window_size=64, batch_size=200, shuffle_buffer=1000)
val_set = windowed_dataset(x_valid, window_size=64, batch_size=200, shuffle_buffer=1000)
model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(60, return_sequences=True),
  tf.keras.layers.LSTM(60),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

threshold_mae = (dt['temp'].max() - dt['temp'].min()) * 10/100

print(threshold_mae)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')<12.45 and logs.get('val_mae')<12.45):
      print("\nMAE model < 10% skala data")
      self.model.stop_training = True
callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(train_set,epochs=100,validation_data = val_set,callbacks=[callbacks])

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Akurasi Model')
plt.ylabel('Mae')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()