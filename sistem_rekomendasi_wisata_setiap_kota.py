# -*- coding: utf-8 -*-
"""Sistem Rekomendasi Wisata Setiap Kota.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m9fqSgIug4Bg3vjBjib_ZoX8D5TyXsM0

#Sistem Rekomendari Destinasi 5 Kota Wisata di Jawa Pada Setiap Kotanya

<hr>
Sumber Data : https://www.kaggle.com/aprabowo/indonesia-tourism-destination

## 1. Mengimpor Library Python
"""

# Commented out IPython magic to ensure Python compatibility.
# Untuk pengolahan data
import pandas as pd
import numpy as np
from zipfile import ZipFile
from pathlib import Path

# Untuk visualisasi data
import seaborn as sns
import matplotlib.pyplot as plt

# %matplotlib inline
sns.set_palette('Set1')
sns.set()

# Untuk pemodelan
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Untuk menghilangkan warnings saat plotting seaborn
import warnings
warnings.filterwarnings('ignore')

# Untuk mengupload file
import os

"""## 2. Menyiapkan Dataset Yang Digunakan

2.1 Mengupload semua Dataset yang akan dipakai
"""

for dirname, _, filenames in os.walk('E:/Project/Bangkit/Dataset/'): #membuka file dataset
    for filename in filenames:
        print(os.path.join(dirname, filename))

"""2.2 Menyimpan setiap dataset kedalam variabel"""

rating = pd.read_csv('tourism_rating.csv')
place = pd.read_csv('tourism_with_id.csv')
user = pd.read_csv('user.csv')

from google.colab import drive
drive.mount('/content/drive')

"""2.3 Membuang Kolom yang tidak Dipakai"""

place = place.drop(['Unnamed: 11','Unnamed: 12'],axis=1)
place.head(5)

"""## 3. Memfilter Sistem Rekomendasi Wisata Berdasarkan Suatu Kota (Input)

3.1 Memilih tempat wisata yang akan dituju
"""

print("Choose City")
print("1. Jakarta")
print("2. Yogyakarta")
print("3. Bandung")
print("4. Semarang")
print("5. Surabaya")
print("")

choose_place = input("Select Number 1-5 (default 1): ")
if choose_place == "2":
  city = 'Yogyakarta'

elif choose_place == "3":
  city = "Bandung"

elif choose_place == "4":
  city = "Semarang"

elif choose_place == "5":
  city = "Surabaya"

else:
    city = "Jakarta"


print("You choose {}" .format(city))

"""3.2 Menampilkan Tempat Wisata berdasarkan kota"""

filter_place = place[place['City'] == city]
filter_place.head(5)

filter_place.info()

"""3.2 Menampilkan Seluruh Data Rating dari kota yang dipilih"""

rating_filter = pd.merge(rating, filter_place[['Place_Id']], how='right', on='Place_Id')
rating_filter.head()

rating_filter.info()

"""# 4.  Data User

4.1 Melihat data user yang pernah mengunjungi wisata di kota yang sudah dipilih
"""

user_filter = pd.merge(user, rating_filter[['User_Id']], how='right', on='User_Id').drop_duplicates().sort_values('User_Id')
user_filter.head(10)

"""4.2 Melihat dataset user yang pernah memberi rating pada wisata di kota yang sudah dipilih"""

user_filter.shape

"""# 5.  Eksplorasi Data

5.1 Visualisasi perbandingan Jumlah Kategori Wisata
"""

plt.title(f'Several Tourist Attraction Category \nfrom {city} \n\n', fontsize=12, weight='bold')

plt.rcParams["figure.figsize"] = (5,5)

unique_filter_categories = filter_place['Category'].unique()

#Mengambil nilai jumlah kategori
categories_filter_counts = filter_place['Category'].value_counts()


#Pie Chart
plt.pie(filter_place['Category'].value_counts(), autopct=lambda p: '{:.1f}%\n({:.0f})'.format(p, p * sum(categories_filter_counts) / 100),
        wedgeprops={'edgecolor': 'black'}, counterclock=False, shadow=True, startangle=25,
        radius=1.3, labels=unique_filter_categories, textprops={'fontsize': 8})
plt.tight_layout()
plt.show()

"""5.2 Visualisasi distribusi harga masuk tempat wisata"""

plt.figure(figsize=(7,3))
sns.boxplot(x = filter_place['Price'])
plt.title('{} Attraction Entry Price Distribution Range'.format(city), pad=20)
plt.show()

"""5.3 Tempat wisata dengan jumlah rating terbanyak"""

# Membuat dataframe berisi lokasi dengan jumlah rating terbanyak
top_10_filter = rating_filter['Place_Id'].value_counts().reset_index()[0:10]
top_10_filter = pd.merge(top_10_filter, filter_place[['Place_Id','Place_Name']], how='left', left_on='index', right_on='Place_Id')

# Membuat visualisasi wisata dengan jumlah rating terbanyak
plt.figure(figsize=(8,5))
sns.barplot(x='Place_Id_x', y='Place_Name', data=top_10_filter)
plt.title('Top Attraction Rating Number In {}'.format(city), pad=20)
plt.ylabel('Attraction Name')
plt.xlabel('Total Rating')
plt.show()

"""5.4 Rata Rata Harga Tiket Masuk Berdasarkan Kategori"""

price_category = filter_place.groupby("Category").agg({'Price': 'mean'})
price_category = price_category.reset_index()
price_category = price_category.rename(columns={'Price' : 'Mean Price'})
price_category = price_category.sort_values(by='Mean Price', ascending=False)
price_category.style.hide_index().format({'Mean Price': '{:.2f}'})

"""# 6. Pemodelan dengan Neural Network


"""

# Select relevant features
data_model = filter_place[['Place_Name','City', 'Price','Rating', 'Category','Description']].copy()

# Rescale the ratings to be between 1 and 5
data_model['Rating'] = data_model['Rating'].apply(lambda x: round(x / 2) if x <= 10 else 5)

# Handle duplicates and missing data
data_model.drop_duplicates(inplace=True)
data_model.dropna(inplace=True)

# Split into features and target
X = data_model[['City', 'Price']]
y = data_model['Rating']

# Convert City to one-hot encoding
X = pd.get_dummies(X, columns=['City'])

# Convert y to categorical
y = tf.keras.utils.to_categorical(y - 1, num_classes=5)

# Split into train, validation, and test sets
X_train, X_val_test, y_train, y_val_test = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_val_test, y_val_test, test_size=0.33, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# Build the neural network model
model = Sequential()
model.add(Dense(32, activation='relu', input_shape=(X_train.shape[1],)))
model.add(Dense(16, activation='relu'))
model.add(Dense(5, activation='softmax'))  # 5 classes

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Fit the model
history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=32)

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)

print('Train Accuracy: ', max(history.history['accuracy']))
print('Validation Accuracy: ', max(history.history['val_accuracy']))
print('Train Loss: ', min(history.history['loss']))
print('Validation Loss: ', min(history.history['val_loss']))
print('Test Accuracy: ', accuracy)
print('Test Loss: ', loss)

"""# Graph A"""

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.legend()
plt.title('Accuracy')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.title('Loss')

plt.show()