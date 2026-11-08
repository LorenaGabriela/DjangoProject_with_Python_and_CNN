from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from joblib import load
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from reportlab.lib.utils import ImageReader
from .models import Pacienti, Ecografii
from .forms import MedicRegistrationForm, LoginForm, PacientiForm, MamografiiForm
from django.http import FileResponse, JsonResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import os
import cv2
import numpy as np
from skimage import measure
from PIL import Image, ImageDraw
from tensorflow.keras.models import load_model
from joblib import load

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

def predict_new_image(image_path):
    model = load_model(r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\ultrasounds_project\segmentare.h5')
    new_image1 = cv2.imread(image_path)
    new_image = cv2.cvtColor(new_image1, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(new_image, (128,128))
    # Adăugarea unei dimensiuni suplimentare pentru a se potrivi cu așteptările modelului (batch_size, height, width, channels)
    image_input = np.expand_dims(resized_image, axis=(0, -1))
    # Normalizarea imaginii
    image_input = image_input / 255.0

    # Aplicarea modelului pentru segmentare
    segmentation_result = model.predict(image_input)
    # Eliminarea dimensiunilor suplimentare
    # Dacă segmentation_result are 3 dimensiuni, eliminăm dimensiunea corespunzătoare canalelor
    if segmentation_result.ndim == 3:
        segmentation_result = segmentation_result[:, :, 0]
    elif segmentation_result.ndim == 4:
        segmentation_result = segmentation_result[0, :, :, 0]
    # Post-procesarea segmentării pentru a determina prezența pixeli tumorali
    threshold = 0.5
    segmentation_binary = (segmentation_result > threshold).astype(np.uint8)

    # Determinarea prezenței pixeților tumorali
    if np.any(segmentation_binary):
        predicted_class = "Afectată"
    else:
        predicted_class = "Neafectată"
    overlayed_image = overlay_contour(resized_image, segmentation_binary)
    # probabilities = model.predict_proba(normalized_image.reshape(1, -1))
    #
    # predicted_class = model.predict(normalized_image.reshape(1, -1))
    # max_score = np.max(probabilities)

    return predicted_class,overlayed_image


# model = r'C:\Users\Lori\PycharmProjects\ImageCLASSIFIER\ultrasounds_project\segmentare.h5'


def predict(request, pacient_id, mamografie_id):
    pacient = Pacienti.objects.get(medic=request.user, id=pacient_id)
    mamografie = Ecografii.objects.get(pacient=pacient, id=mamografie_id)

    if request.method == 'POST':
        image_path = mamografie.fisier.path

        if image_path and os.path.exists(image_path):
            predicted_class = predict_new_image(image_path)[0]
            if predicted_class == "Afectată":
                diagnostic = "Ecografia prezinta  afectiune!"
            elif predicted_class == "Neafectată":
                diagnostic = "Ecografia nu prezinta afectiune!"

            mamografie.diagnostic = diagnostic
            # mamografie.ecografie_segmentata = predict_new_image(image_path)[1]
            predicted_class, overlayed_image = predict_new_image(image_path)
            # Convertește imaginea în PIL într-un șir de octeți
            buffered = io.BytesIO()
            overlayed_image.save(buffered, format="JPEG")  # sau formatul dorit

            # Salvează șirul de octeți într-un obiect ContentFile
            overlayed_image_file = ContentFile(buffered.getvalue(), name='overlayed_image.jpg')

            # Actualizează câmpul de fișier al modelului cu noua imagine
            mamografie.ecografie_segmentata.save('overlayed_image.jpg', overlayed_image_file)

            mamografie.save()
            mamografii = Ecografii.objects.filter(pacient=pacient)
            form = MamografiiForm
            context = {'form_mamografii': form, 'pacient': pacient, 'mamografii': mamografii, 'predicted_class':predicted_class}
            return render(request, 'medical/mamografii1.html', context)
        else:
            return JsonResponse({'error': 'Calea către fișierul imaginii este lipsă sau invalidă.'}, status=400)
    else:
        return JsonResponse({'error': 'Cererea trebuie să fie de tip POST.'}, status=405)


def generare_raport(request, pacient_id):
    buf = io.BytesIO()
    c = canvas.Canvas(buf,pagesize=letter,bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch,inch)
    textob.setFont("Helvetica", 14)
    pagina_noua = False

    pacient = Pacienti.objects.get(medic=request.user, id = pacient_id )
    c.drawString(inch, inch, "RAPORT")
    y = inch

    if pacient:
        y += 40
        c.drawString(inch, y, f"Pacient: {pacient.nume_pacient} {pacient.prenume_pacient}")
        y += 20
        c.drawString(inch, y, f"Email Pacient: {pacient.email_pacient}")
        y += 20
        c.drawString(inch, y, f"Telefon Pacient: {pacient.telefon_pacient}")
        y += 20
        c.drawString(inch, y, f"Data nasterii Pacient: {pacient.data_nastere}")
        y += 20
        c.drawString(inch, y, f"Sex Pacient: {pacient.sex_pacient}")
        y += 20
    mamografii = Ecografii.objects.filter(pacient=pacient)

    for mamografie in mamografii:
        if (y + 240) > 750:  # Ajustat pentru a ține cont de înălțimea adăugată
            c.showPage()
            y = inch
        y += 20
        c.drawString(inch, y, f"Ecografie: {mamografie.data_incarcare}")
        y += 20  # Avansăm puțin pentru diagnostic
        c.drawString(inch, y, f"Diagnostic: {mamografie.diagnostic}")
        img = ImageReader(mamografie.fisier.path)
        c.drawImage(img, inch, y + 20, width=128, height=128)  # Afișează imaginea
        # Imaginea ecografiei segmentate
        if mamografie.ecografie_segmentata:
            img_ecografie_segmentata = ImageReader(mamografie.ecografie_segmentata.path)
            c.drawImage(img_ecografie_segmentata, inch + 150, y + 20, width=128, height=128)
        y += 220  # Ajustează pentru înălțimea totală ocupată


        print(y)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=f'raport_{pacient.nume_pacient}_{pacient.prenume_pacient}.pdf')


def home(request):
    return render(request, 'medical/home.html')


@csrf_protect
def register_medic(request):
    form = MedicRegistrationForm()

    if request.method == 'POST':
        form = MedicRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_medic')
    context = {'registerform': form}
    return render(request, 'medical/register_medic.html',context=context)


def login_medic(request):
    if request.method == 'GET' and not request.user.is_anonymous:
        return redirect("pacienti")
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            messages.success(request, "You are Logged In")
            if user is not None:
                auth.login(request, user)
                return redirect("pacienti")
    context = {'loginform': form}
    return render(request, 'medical/login_medic.html', context=context)


def logout_user(request):
    logout(request)
    return redirect('home')


@login_required(login_url="login_medic")
def pacienti(request):
    pacienti = Pacienti.objects.filter(medic = request.user)
    form = PacientiForm()
    context = {'pacienti' : pacienti, "form" : form}
    print(request)
    print(request.user)
    return render(request, 'medical/pacienti.html', context)


def adaugapacienti(request):
    if request.method == 'POST':
        form = PacientiForm(request.POST or None)

        if form.is_valid():
            pacient = form.save(commit=False)
            print(request.user)
            pacient.medic = request.user
            pacient.save()

            form = PacientiForm()
            pacienti = Pacienti.objects.filter(medic = request.user)
            context = {'pacienti': pacienti,'form': form}
            return render(request,'medical/adauga_pacienti.html',context)
    else:
        form = PacientiForm()
        pacienti = Pacienti.objects.filter(medic = request.user)
        context = {'persoane': pacienti, 'form': form}
        return render(request, 'medical/adauga_pacienti.html',context)
#
# @require_http_methods(["DELETE"])
# def stergepacienti(request,id):
#
#     pacient = Pacienti.objects.get(pk=id)
#     pacient.delete()
#     return redirect('pacienti')
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from .models import Pacienti

@require_http_methods(["DELETE"])
def stergepacienti(request, id):
    try:
        pacient = Pacienti.objects.get(pk=id)
        pacient.delete()
        return JsonResponse({'message': 'Pacient șters cu succes'})
    except Pacienti.DoesNotExist:
        return JsonResponse({'error': 'Pacientul nu a fost găsit'}, status=404)


def editeaza_pacient(request, id):
    pacient = get_object_or_404(Pacienti, pk=id)
    if request.method == 'POST':
        form = PacientiForm(request.POST, instance=pacient)
        if form.is_valid():
            form.save()
            return redirect('pacienti')
    else:
        form = PacientiForm(instance=pacient)
    return render(request, 'medical/editeaza_pacient.html', {'form_edit_pacienti': form})


def upload_mamografie_pacient1(request,pacient_id):
    pacient = Pacienti.objects.filter(id=pacient_id).first()
    form = MamografiiForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        form = MamografiiForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.pacient = pacient
            uploaded_file.save()
            context = {'form': form, 'uploaded_file': uploaded_file,'pacient' : pacient}
            return render(request, 'medical/upload_mamografie_pacient1.html',
                          context)

    return render(request, 'medical/upload_mamografie_pacient1.html', {'form': form, 'pacient': pacient})


def mamografii1(request,pacient_id):
    pacient = Pacienti.objects.filter(id=pacient_id).first()
    mamografii = Ecografii.objects.filter(pacient=pacient)
    form = MamografiiForm()
    context = {'form_mamografii': form,'pacient' : pacient, 'mamografii' : mamografii}
    return render(request, 'medical/mamografii1.html', context)


