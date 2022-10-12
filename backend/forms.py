from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import Shipping, Customer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField


class ShippingForm(forms.ModelForm):

    class Meta:
        model = Shipping
        fields = (
            'payment',
            'city',
            'warehouse',
            'comment',
        )

        widgets = {
            'payment': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': "Коментар до замовлення (не обов'язково)", 'rows': "4"
            }),
        }

        labels = {
            'payment': 'Оплата',
            'city': 'Місто',
            'warehouse': 'Відділення НП',
            'comment': 'Коментар',
        }


class CustomerForm(forms.ModelForm):
    phone = PhoneNumberField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'XXX-XXX-XX-XX'
    }), label="Номер телефону")
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'example@gmail.com'
    }), label="Email")
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': "Ім'я"}), label="Ім'я")
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': "Прізвище"}), label="Прізвище")

    class Meta:
        model = Customer
        fields = (
            'first_name',
            'last_name',
            'phone',
            'email',)


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('password1',
                  'password2',)

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
