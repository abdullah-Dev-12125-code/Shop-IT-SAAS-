from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Seller


User = get_user_model()


class SellerRegisterForm(forms.Form):
    email_linked = forms.EmailField(label="Email Address")
    phone = forms.CharField(max_length=20)
    store_name = forms.CharField(max_length=150)
    parent_organization = forms.CharField(max_length=150, required=False)
    email_vendor = forms.EmailField(label="Vendor Email Address")
    address = forms.CharField(widget=forms.Textarea)
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email_linked(self):
        email = self.cleaned_data["email_linked"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_store_name(self):
        store_name = self.cleaned_data["store_name"].strip()
        if Seller.objects.filter(store_name__iexact=store_name).exists():
            raise forms.ValidationError("A seller with this store name already exists.")
        return store_name

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
            return cleaned_data

        if password1:
            try:
                validate_password(password1)
            except ValidationError as exc:
                for message in exc.messages:
                    self.add_error("password1", message)

        return cleaned_data

    def save(self):
        with transaction.atomic():
            user = User.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data["email_linked"],
                password=self.cleaned_data["password1"],
            )

            seller = Seller.objects.create(
                user=user,
                store_name=self.cleaned_data["store_name"],
                parent_organization=self.cleaned_data.get("parent_organization", ""),
                phone=self.cleaned_data["phone"],
                email_linked=self.cleaned_data["email_linked"],
                email_vendor=self.cleaned_data["email_vendor"],
                address=self.cleaned_data["address"],
                is_active=True,
            )

        return seller


class SellerLoginForm(forms.Form):
    username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)