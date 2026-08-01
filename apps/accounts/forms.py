from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'id': 'username_input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'password_input'})
    )

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture']

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Registered Email Address'})
    )
