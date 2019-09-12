from django import forms

class ImportTradeshowForm(forms.Form):
    file = forms.FileField()
