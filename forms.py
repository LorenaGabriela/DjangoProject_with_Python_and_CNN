from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import TextInput, PasswordInput
from .models import Pacienti, Ecografii


class MedicRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())





GENDER_CHOICES = [
    ('F', 'Feminin'),
    ('M', 'Masculin'),
]

class PacientiForm(forms.ModelForm):
    sex_pacient = forms.ChoiceField(choices=GENDER_CHOICES, label='Sex', widget=forms.RadioSelect)

    class Meta:
        model = Pacienti
        fields = ['nume_pacient', 'prenume_pacient', 'email_pacient', 'telefon_pacient', 'data_nastere', 'sex_pacient']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nume_pacient'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'nume '})
        self.fields['prenume_pacient'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'prenume '})
        self.fields['email_pacient'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'email '})
        self.fields['telefon_pacient'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'telefon '})
        self.fields['data_nastere'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'data nastere'})
        self.fields['sex_pacient'].widget.attrs.update({'class': 'my-custom-class'})
class MamografiiForm(forms.ModelForm):

    class Meta:
        model = Ecografii
        fields = ['fisier', 'descriere', 'data_incarcare', 'diagnostic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fisier'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'fisier '})
        self.fields['descriere'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'descriere '})
        self.fields['data_incarcare'].widget.attrs.update({'class': 'my-custom-class', 'placeholder': 'data_incarcare '})
        self.fields['diagnostic'].widget.attrs.update({'class': 'my-custom-class','placeholder': 'diagnostic '})

