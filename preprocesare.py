import matplotlib.pyplot as plt

# Lista cu căile către fiecare imagine
cale_imagini = [
    (r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\benign\benign (7).png", "Imagine originala-benign"),
    (r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\benign\benign (7)_mask.png","Masca-benign"),
     (r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\malignant\malignant (23).png","Imagine originala-maligna"),
     (r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\malignant\malignant (23)_mask.png","Masca-benign"),
     (r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\normal\normal (22).png","Imagine originala-normal"),
     (r"C:\Users\Lori\Downloads\Dataset_BUSI_with_GT\normal\normal (22)_mask.png","Masca-normal"),
]

# Numărul total de imagini
numar_imagini = len(cale_imagini)

# Numărul de coloane și rânduri pentru subploturi
numar_coloane = 2
numar_randuri = numar_imagini // numar_coloane

# Creează subploturi
fig, axs = plt.subplots(numar_randuri, numar_coloane, figsize=(10, 6))

# Parcurgeți imaginile și titlurile și plasați-le în subploturi
for i, (cale_imagine, titlu) in enumerate(cale_imagini):
    rand = i // numar_coloane
    coloana = i % numar_coloane
    ax = axs[rand, coloana]

    # Încărcați imaginea și plasați-o în subplot
    imagine = plt.imread(cale_imagine)
    ax.imshow(imagine, cmap="gray")
    ax.axis("off")

    # Adăugați titlul imaginii
    ax.set_title(titlu)

# Ajustați spațiile între subploturi pentru o mai bună vizibilitate
plt.tight_layout()

# Afișați subploturile
plt.show()