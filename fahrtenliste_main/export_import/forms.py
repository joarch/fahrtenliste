from django import forms


class UploadAdresseFileForm(forms.Form):
    file = forms.FileField()
    format = forms.CharField()
