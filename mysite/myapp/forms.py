from django import forms
from .models import Product
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)
    #     # Handle the user argument as needed
    #     if user:
    #         self.fields['seller'].initial = user

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'file']
    # class Meta:
    #     model = Product
    #     fields = '__all__'


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "first_name", "email", "password1", "password2"]
    

    # def clean(self):
    #     cleaned_data = super().clean()
    #     password1 = cleaned_data.get('password1')
    #     password2 = cleaned_data.get('password2')

    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("Passwords do not match!")
    #     print("Cleaned data : {}".format(cleaned_data))
    #     return cleaned_data
    """
    By using the clean_password2() method, you can rely on Django's built-in form
    validation and eliminate the need for the clean() method.
    """
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")

        return password2
