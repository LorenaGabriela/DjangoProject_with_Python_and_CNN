from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = [
    ('F', 'Feminin'),
    ('M', 'Masculin'),
]
class Pacienti(models.Model):
    medic = models.ForeignKey(User, on_delete=models.CASCADE)
    nume_pacient = models.CharField(max_length=100)
    prenume_pacient = models.CharField(max_length=100)
    email_pacient = models.EmailField(max_length=100)
    telefon_pacient = models.CharField(max_length=12)
    data_nastere = models.DateField()
    sex_pacient = models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        db_table = 'Pacienți'
    def __str__(self):
        return self.nume_pacient + ' ' + self.prenume_pacient


class Ecografii(models.Model):
    pacient = models.ForeignKey(Pacienti, on_delete=models.CASCADE)
    fisier = models.ImageField(null=True,blank=True)
    descriere = models.TextField(blank=True)
    data_incarcare = models.DateField()
    diagnostic = models.CharField(max_length=100,blank=True)
    ecografie_segmentata = models.ImageField(null=True,blank=True)

    class Meta:
        db_table = 'Ecografii'
    def __str__(self):
        return f"{self.pacient} - {self.fisier.name}"




