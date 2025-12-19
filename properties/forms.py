from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import LandlordApplication


class SignUpForm(UserCreationForm):
    """Simple signup form – user is a tenant by default."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LandlordApplicationForm(forms.ModelForm):
    """Form for landlords to apply and be verified."""

    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your full legal name',
            'required': True
        }),
        help_text="Your full name as it appears on your ID document"
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your.email@example.com',
            'required': True
        }),
        help_text="We'll use this to contact you about your application"
    )

    phone = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '+254 7XX XXX XXX',
            'required': True
        }),
        help_text="Include country code (e.g., +254 for Kenya)"
    )

    id_document = forms.FileField(
        label="ID Document",
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-lg',
            'accept': '.pdf,.jpg,.jpeg,.png',
            'required': True
        }),
        help_text="Upload a clear photo or scan of your National ID, Passport, or KRA PIN certificate (PDF, JPG, or PNG)"
    )

    county = forms.CharField(
        label="County",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g., Nairobi, Mombasa, Kisumu',
            'list': 'county-list'
        }),
        required=False,
        help_text="The county where you own property"
    )

    sub_county = forms.CharField(
        label="Sub-county",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g., Westlands, Nyali',
            'list': 'subcounty-list'
        }),
        required=False
    )

    estate = forms.CharField(
        label="Estate/Area",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g., Kilimani, Karen, Westlands',
            'list': 'estate-list'
        }),
        required=False,
        help_text="The specific estate or area where your property is located"
    )

    class Meta:
        model = LandlordApplication
        fields = [
            "full_name",
            "email",
            "phone",
            "id_document",
            "county",
            "sub_county",
            "estate",
        ]


