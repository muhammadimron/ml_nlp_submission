# -*- coding: utf-8 -*-
"""NLP Submission Muhammad Imron.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oce9rzlLt4MXeulCSQCvysFH0a8Elq-H

Hallo, Kak Reviewer. 

Perkenalkan, namaku Muhammad Imron, bisa dipanggil Imron. Di submission NLP ini, aku pakai dataset dari UCI Machine Learning, kak, namanya News_Final.csv. Rencananya di submission ini aku bakalan nerapin multiclass text classification tentang nyari tipe berita berdasarkan headlinenya.

Mohon bantuannya kak, untuk direview.

Terima kasih

---

https://archive.ics.uci.edu/ml/datasets/News+Popularity+in+Multiple+Social+Media+Platforms#
"""

# Import library yang dibutuhkan
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
import os

from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Import dataset
df = pd.read_csv('/content/drive/MyDrive/NLP_Submission/News_Final.csv')
df.tail()

plt.hist(df['Topic'])
plt.show()

# One Hot Encoding
category = pd.get_dummies(df.Topic)
new_df = pd.concat([df, category], axis=1)
new_df = new_df.sample(frac=1).reset_index()
new_df = new_df.drop(columns=['index', 'IDLink', 'Topic', 'Title', 
                              'Source', 'PublishDate', 'SentimentTitle', 
                              'SentimentHeadline', 'Facebook', 
                              'GooglePlus', 'LinkedIn'])
new_df.Headline = new_df.Headline.astype(str)
new_df

# Train Test Splitting
sentence = new_df['Headline'].values
label = new_df[['economy', 'microsoft', 'obama', 'palestine']].values
sentence_train, sentence_test, label_train, label_test = train_test_split(sentence, label, test_size=0.2)

# Tokenization dan Sequencing
tokenizer = Tokenizer(num_words=10000, oov_token='x')
tokenizer.fit_on_texts(sentence_train)
tokenizer.fit_on_texts(sentence_test)

sekuens_train = tokenizer.texts_to_sequences(sentence_train)
sekuens_test = tokenizer.texts_to_sequences(sentence_test)

padded_train = pad_sequences(sekuens_train)
padded_test = pad_sequences(sekuens_test)

# Membangun arsitektur model dan compile model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=10000, output_dim=1000),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.15),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(4, activation='softmax')
])
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# Sebelum melakukan fitting, saya coba menambahkan callbacks untuk checkpoint dan earlystopping
models_dir = 'save_models'
if not os.path.exists(models_dir):
  os.makedirs(models_dir)

# Checkpointer
checkpointer = ModelCheckpoint(filepath=os.path.join(models_dir, 'model.hdf5'),
                               monitor='val_accuracy', mode='max',
                               verbose=1, save_best_only=True)

# Reduce Learning Rate
reduce_learning_rate = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001)

# EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', mode='min',
                               verbose=1, patience=3)

# Membuat callback
callbacks = [early_stopping, checkpointer, reduce_learning_rate]

# Fitting model
num_epochs = 30
history = model.fit(padded_train, 
                    label_train, 
                    epochs=num_epochs,
                    validation_data=(padded_test, label_test),
                    callbacks=callbacks)

# Plot Loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='lower left')
plt.show()

# Plot Akurasi
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()