from django import forms
from .models import File, Group
from django.contrib.auth.models import User

class FileForm(forms.ModelForm):
    class Meta:
        model=File
        fields = ['group', 'file']


class GroupForm(forms.ModelForm):
    use_required_attribute = False
    users = forms.ModelMultipleChoiceField(
    queryset=User.objects.all(),
    widget=forms.SelectMultiple(attrs={'class': 'form-checkbox'})
    )
    class Meta:
        model= Group
        fields = ['name', 'users']
