from django import forms
from cadastros.models import *

class CadastrarJogadorForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput(attrs={'maxlength':'250'}))    
    telefone = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'maxlength':'20'}))
    foto = forms.ImageField(required=False)
    url_foto = forms.CharField(widget=forms.TextInput(attrs={'maxlength': '250'}))




class AnotarGolForm(forms.Form):
    # tempo = forms.CharField(widget=forms.TextInput(attrs={'maxlength':'250'}))    
    gol = forms.CharField()
    assistencia = forms.CharField(); 
    
    # partida = 