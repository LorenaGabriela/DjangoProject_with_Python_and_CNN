import numpy as np
import tensorflow as tf
import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from skimage import metrics
from tqdm import tqdm
from PIL import Image

from sklearn.model_selection import train_test_split

import tensorflow as tf

from tensorflow.keras.preprocessing.image import img_to_array, load_img

root_dir = r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT"

folders = ["benign", "malignant", "normal"]

image_paths, labels, mask_paths = [], [], []

for folder in folders:
    files = os.listdir(os.path.join(root_dir, folder))
    for file in files:
        if "mask_" in file:
            continue
        elif "mask" in file:
            mask_paths.append(os.path.join(root_dir, folder, file))
        else:
            image_paths.append(os.path.join(root_dir, folder, file))
            labels.append(folder)

# df = pd.DataFrame({"image_path": image_paths, "mask_path": mask_paths,"label": labels})
# print(df.head())
# print(df["label"].value_counts())

def load_image(path):
    img = load_img(path, target_size=(128, 128),color_mode='grayscale')
    image_array = img_to_array(img)
    image_array /= 255.
    return image_array
images = []
masks = []

for image_path, mask_path in tqdm(zip(image_paths, mask_paths)):
    image = load_image(image_path)
    images.append(image)

    mask = load_image(mask_path)
    masks.append(mask)
images = np.array(images)
masks = np.array(masks)


images = images[:-133]
masks = masks[:-133]
X_train, X_test, y_train, y_test = train_test_split(images, masks, test_size=0.1, random_state=42)
# print("Dimensiunea lui X_train:", X_train.shape)
# print("Dimensiunea lui X_test:", X_test.shape)
# print("Dimensiunea lui y_train:", y_train.shape)
# print("Dimensiunea lui y_test:", y_test.shape)

# # Încarcă modelul de segmentare
# model = tf.keras.models.load_model('best_model11.h5')
#
# # Încarcă imaginile de testare și ground truth
# # Încarcă și preprocesează imaginile aici
# # După ce ai antrenat modelul și ai folosit datele de testare pentru a face predicții
# predicted_masks = model.predict(X_test)
# # Ensure predicted masks have binary values
# predicted_masks = (predicted_masks > 0.5).astype(np.float32)
def dice_coef(y_true, y_pred):
    smooth = 1e-5
    intersection = np.sum(y_true * y_pred)
    return (2. * intersection + smooth) / (np.sum(y_true) + np.sum(y_pred) + smooth)

def iou_score(y_true, y_pred):
    intersection = np.logical_and(y_true, y_pred)
    union = np.logical_or(y_true, y_pred)
    iou = np.sum(intersection) / np.sum(union)
    return iou
# # Ensure predicted masks have binary values
# predicted_masks = (predicted_masks > 0.5).astype(np.float32)
#
# # Calculează coeficientul Dice între segmentările prezise și cele reale
# dice_scores = []
# for true_mask, pred_mask in zip(y_test, predicted_masks):
#     # Reshape pred_mask to match the shape of true_mask
#     pred_mask = np.squeeze(pred_mask)
#     pred_mask = pred_mask[..., 0]  # Take only one channel if there are multiple channels
#     dice_scores.append(dice_coef(true_mask, pred_mask))
#
# average_dice_score = np.mean(dice_scores)
# print("Dice Score :", average_dice_score)
#
# # Calculează IoU între segmentările prezise și cele reale
# iou_scores = []
# for true_mask, pred_mask in zip(y_test, predicted_masks):
#     # Reshape pred_mask to match the shape of true_mask
#     pred_mask = np.squeeze(pred_mask)
#     pred_mask = pred_mask[..., 0]  # Take only one channel if there are multiple channels
#     iou_scores.append(iou_score(true_mask, pred_mask))
#
# average_iou_score = np.mean(iou_scores)
# print("IoU Score :", average_iou_score)
# Încărcați modelul antrenat

# Dice Score (Medie): 0.6291182393735952
# IoU Score (Medie): 0.09341826782946137
# model = tf.keras.models.load_model(r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\segmentare_simpla_ecografii_1\unet_model.h5', custom_objects={'dice_coef': dice_coef})

# Dice Score (Medie): 0.5847845861366291
# IoU Score (Medie): 0.0943382675410343
# model = tf.keras.models.load_model(r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\segmentare_simpla_ecografii_1\best_model_segm.h5', custom_objects={'dice_coef': dice_coef})


model = tf.keras.models.load_model(r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\segmentare_simpla_ecografii_1\best_model_segm_60_epoci.h5', custom_objects={'dice_coef': dice_coef})

# Print the shapes of y_true and y_pred to debug the shape mismatch
print("Shape of y_true:", y_test.shape)


# Efectuați predicții pe datele de test
predicted_masks = model.predict(X_test)
print("Shape of y_pred:", predicted_masks.shape)

import numpy as np

def dice_coef(y_true, y_pred):
    smooth = 1e-5
    intersection = np.sum(y_true * y_pred)
    return (2. * intersection + smooth) / (np.sum(y_true) + np.sum(y_pred) + smooth)

def iou_score(y_true, y_pred):
    intersection = np.logical_and(y_true, y_pred)
    union = np.logical_or(y_true, y_pred)
    iou = np.sum(intersection) / np.sum(union)
    return iou

# Calculați scorurile Dice și IoU între măștile prezise și cele adevărate
dice_scores = [dice_coef(true_mask, pred_mask) for true_mask, pred_mask in zip(y_test, predicted_masks)]
iou_scores = [iou_score(true_mask, pred_mask) for true_mask, pred_mask in zip(y_test, predicted_masks)]

# Calculați scorurile medii
average_dice_score = np.mean(dice_scores)
average_iou_score = np.mean(iou_scores)

print("Dice Score (Medie):", average_dice_score)
print("IoU Score (Medie):", average_iou_score)
# Calculați scorurile maxime pentru Dice și IoU
best_dice_score = np.max(dice_scores)
best_iou_score = np.max(iou_scores)
bad_dice_score = np.min(dice_scores)
bad_iou_score = np.min(iou_scores)

print("Cel mai bun Dice Score:", best_dice_score)
print("Cel mai bun IoU Score:", best_iou_score)
print("Cel mai scazut Dice Score:", bad_dice_score)
print("Cel mai scazut IoU Score:", bad_iou_score)

# Identificarea indexului pentru imaginea cu cel mai bun rezultat
index_best_dice = np.argmax(dice_scores)
index_best_iou = np.argmax(iou_scores)

# Identificarea indexului pentru imaginea cu cel mai prost rezultat
index_worst_dice = np.argmin(dice_scores)
index_worst_iou = np.argmin(iou_scores)

# Obțineți căile către imaginile cu cel mai bun și cel mai prost rezultat
path_best_dice = image_paths[index_best_dice]
path_best_iou = image_paths[index_best_iou]
path_worst_dice = image_paths[index_worst_dice]
path_worst_iou = image_paths[index_worst_iou]

print("Calea către imaginea cu cel mai bun Dice Score:", path_best_dice)
print("Calea către imaginea cu cel mai bun IoU Score:", path_best_iou)
print("Calea către imaginea cu cel mai slab Dice Score:", path_worst_dice)
print("Calea către imaginea cu cel mai slab IoU Score:", path_worst_iou)

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
from skimage import measure
from PIL import Image, ImageDraw

# Definește funcția overlay_contour
def overlay_contour(image, mask, threshold=0.5):
    mask = (mask > threshold).astype(np.uint8)
    contours = measure.find_contours(mask, 0.5)
    image_pil = Image.fromarray(image.astype(np.uint8))
    image_pil = image_pil.convert("RGB")
    draw = ImageDraw.Draw(image_pil)

    for contour in contours:
        contour = np.flip(contour, axis=1)
        contour = np.round(contour).astype(int)
        for i in range(len(contour) - 1):
            draw.line([(contour[i][0], contour[i][1]), (contour[i + 1][0], contour[i + 1][1])], fill="red", width=2)

    return image_pil

# Funcția pentru a încărca și preprocesa o imagine
def load_and_preprocess_image(path, target_size=(128, 128)):
    img = load_img(path, target_size=target_size, color_mode='grayscale')
    img_array = img_to_array(img)
    img_array = img_array / 255.0  # Normalizare
    return img_array

# Calea către modelul salvat
model_path = r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\segmentare_simpla_ecografii_1\best_model_segm_60_epoci.h5'

# Încarcă modelul de segmentare
model = tf.keras.models.load_model(model_path, custom_objects={'dice_coef': dice_coef})

# Căile către imaginile de test
image_paths = [
   r'C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\benign\benign (100).png',
    r'C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\malignant\malignant (15).png',

    r'C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\normal\normal (2).png'
]
mask_paths = [
    r'C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\benign\benign (100)_mask.png',
    r'C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\malignant\malignant (15)_mask.png',
    r'C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\normal\normal (2)_mask.png'
]
# Încarcă și preprocesează imaginile de test și măștile originale
X_test = np.array([load_and_preprocess_image(path) for path in image_paths])
y_true = np.array([load_and_preprocess_image(path) for path in mask_paths])

# Efectuează predicțiile modelului
predicted_masks = model.predict(X_test)

# Plotează rezultatele
fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(20, 10))

for i in range(3):
    original_image = (X_test[i] * 255).astype(np.uint8).squeeze()  # Convertire la imagine originală
    true_mask = (y_true[i] * 255).astype(np.uint8).squeeze()  # Convertire la masca originală
    predicted_mask = predicted_masks[i].squeeze()  # Scoate dimensiunea canalului

    # Imaginea originală
    axes[i, 0].imshow(original_image, cmap='gray')
    axes[i, 0].set_title("Imaginea originală")
    axes[i, 0].axis('off')

    # Imaginea cu conturul măștii prezise
    overlaid_image_pred = overlay_contour(original_image, predicted_mask)
    axes[i, 1].imshow(overlaid_image_pred)
    axes[i, 1].set_title("Imaginea prezisă de model")
    axes[i, 1].axis('off')

    # Imaginea cu conturul măștii originale
    overlaid_image_true = overlay_contour(original_image, true_mask)
    axes[i, 2].imshow(overlaid_image_true)
    axes[i, 2].set_title("Imaginea originala cu contur")
    axes[i, 2].axis('off')

    # Masca prezisă
    axes[i, 3].imshow(predicted_mask, cmap='gray')
    axes[i, 3].set_title("Masca prezisa")
    axes[i, 3].axis('off')

    axes[i, 4].imshow(true_mask, cmap='gray')
    axes[i, 4].set_title("Masca originala")
    axes[i, 4].axis('off')

plt.tight_layout(pad=2.0)
plt.show()