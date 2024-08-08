from django import forms
from .models import Product_Add, Product
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
class ProductAddForm(forms.ModelForm):

    product_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'section-redact-address-select-block'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'section-redact-address-block-gray-images'}))
    product_town = forms.CharField(widget=forms.TextInput(attrs={'class': 'section-redact-address-block-gray-select'}))
    product_distr = forms.CharField(widget=forms.TextInput(attrs={'class': 'section-redact-address-select-block'}))
    product_employee = forms.CharField(widget=forms.TextInput(attrs={'class': 'section-redact-address-select-block'}))

    class Meta:
        model = Product_Add
        fields = ('product_name', 'product_descr', 'image', 'product_town', 'product_distr', 'product_addr', 'product_comm', 'product_price', 'product_employee')



class ProductRedactForm(UserChangeForm):
   
    name = forms.CharField(widget=forms.TextInput(attrs={'class': "section-redact-address-select-block"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn-add-images'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': "section-redact-address-select-block"}))
    district = forms.CharField(widget=forms.TextInput(attrs={'class': "section-redact-address-select-block"}))
    employee = forms.CharField(widget=forms.TextInput(attrs={'class': "section-redact-address-select-block"}))


    class Meta:
        model = Product
        fields = ('name', 'product_descr', 'image', 'city', 'district', 'product_addr', 'product_comm', 'employee')




class LoginForm(forms.Form):
    login = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'auth_name', 'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth_password', 'placeholder': 'Пароль'}))