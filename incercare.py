from pickle import dump

import pca as pca
import sys
import sklearn
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
import cv2



def load_images_from_directory(directory):
    images = []
    labels = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            label = os.path.basename(root)
            image = cv2.imread(filepath)
            images.append(image)
            labels.append(int(label))
    return images, labels

train_dir = r"C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\data_final\train"
test_dir = r"C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\data_final\test"

train_images, train_labels = load_images_from_directory(train_dir)
test_images, test_labels = load_images_from_directory(test_dir)
print('s au citit imaginile')

resized_images_train = [cv2.resize(image, (256,256)) for image in train_images]
# Pregătiți datele de intrare pentru antrenare și testare
X_train = np.array([np.array(image, dtype=np.float32).reshape(-1) for image in resized_images_train])
y_train = np.array(train_labels)
print('pregatire train')

resized_images_test = [cv2.resize(image, (256,256)) for image in test_images]
X_test = np.array([np.array(image, dtype=np.float32).reshape(-1) for image in resized_images_test])
y_test = np.array(test_labels)
print('pregatire test')


# ##normalizare
min_value = X_train.min()
max_value = X_train.max()

X_train_normalized = (X_train - min_value) / (max_value - min_value)
X_test_normalized = (X_test - min_value) / (max_value - min_value)
print('s au normalizat')
def normalize_images(images):
    min_value = images.min()
    max_value = images.max()
    normalized_images = (images - min_value) / (max_value - min_value)
    return normalized_images


# X_train_normalized = normalize_images(X_train)
# X_test_normalized = normalize_images(X_test)




# #Acuratețe: 0.7142857142857143
# clf = SVC(kernel='linear')

#Acuratețe: 0.6
# from sklearn.naive_bayes import GaussianNB
# clf = GaussianNB()

#Acuratețe: 0.8
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)

#Acuratețe: 0.7142857142857143
# from sklearn.neighbors import KNeighborsClassifier
# clf = KNeighborsClassifier(n_neighbors=5)

#Acuratețe: 0.6857142857142857
# from sklearn.linear_model import LogisticRegression
# clf = LogisticRegression(max_iter=1000)


clf.fit(X_train_normalized, y_train)
dump(clf, 'random_forest_model2.joblib')
y_pred = clf.predict(X_test_normalized)
print(y_pred.size)

print(set(y_train) - set(y_test))
print(set(y_test) - set(y_train))


accuracy = accuracy_score(y_test, y_pred)
# svm_score = cross_val_score(model, X_train_normalized, y_train, cv=10, scoring='accuracy')
print("Acuratețe:", accuracy)


def predict_new_image(image_path, model, X_train):
    # 1. Încărcați și redimensionați imaginea nouă
    new_image = cv2.imread(image_path)
    resized_image = cv2.resize(new_image, (256, 256))

    # 2. Normalizați imaginea nouă
    min_value = X_train.min()
    max_value = X_train.max()
    normalized_image = (resized_image - min_value) / (max_value - min_value)

    # 3. Realizați predicția și obțineți probabilitățile asociate fiecărei clase
    probabilities = model.predict_proba(normalized_image.reshape(1, -1))

    # 4. Obțineți clasa prezisă și scorul maxim
    predicted_class = model.predict(normalized_image.reshape(1, -1))
    max_score = np.max(probabilities)

    return predicted_class, max_score, probabilities



prediction = predict_new_image(r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\data_final\test\0\mdb011ll.png', clf, X_train)
print("Clasa prezisă pentru imaginea nouă:", prediction)
# Raport de clasificare
print(classification_report(y_test, y_pred))