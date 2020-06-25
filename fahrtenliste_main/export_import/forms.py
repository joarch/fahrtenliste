from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    format_key = forms.CharField()
    typ = forms.CharField()
