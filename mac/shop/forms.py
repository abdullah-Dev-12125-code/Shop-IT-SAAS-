from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class ProfileForm(forms.Form):
    """Form for editing user profile information"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'John',
            'class': 'form-control',
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Doe',
            'class': 'form-control',
        })
    )
    
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell us about yourself...',
            'rows': 4,
            'class': 'form-control',
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '+1 (555) 234-5678',
            'type': 'tel',
            'class': 'form-control',
        })
    )
    
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City, State, ZIP',
            'class': 'form-control',
        })
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )

    banner = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }

        )
    )
    
    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name', '').strip()
        
        if not first_name:
            raise ValidationError('First name is required.')
        
        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters long.')
        
        if not re.match(r"^[a-zA-Z\s'-]+$", first_name):
            raise ValidationError('First name can only contain letters, spaces, hyphens, and apostrophes.')
        
        return first_name
    
    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name', '').strip()
        
        if not last_name:
            raise ValidationError('Last name is required.')
        
        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters long.')
        
        if not re.match(r"^[a-zA-Z\s'-]+$", last_name):
            raise ValidationError('Last name can only contain letters, spaces, hyphens, and apostrophes.')
        
        return last_name
    
    def clean_bio(self):
        """Validate bio"""
        bio = self.cleaned_data.get('bio', '').strip()
        
        if bio and len(bio) > 500:
            raise ValidationError('Bio must not exceed 500 characters.')
        
        return bio
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if phone:
            # Remove common formatting characters
            cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
            
            if not re.match(r'^\+?[0-9]{10,15}$', cleaned):
                raise ValidationError('Please enter a valid phone number.')
        
        return phone
    
    def clean_address(self):
        """Validate address"""
        address = self.cleaned_data.get('address', '').strip()
        
        if address and len(address) < 5:
            raise ValidationError('Please enter a complete address.')
        
        return address
    
    def clean_avatar(self):
        """Validate avatar image"""
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            # Check file size (5MB max)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must not exceed 5MB.')
            
            # Check file format
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar.content_type not in allowed_formats:
                raise ValidationError('Please upload a valid image file (JPG, PNG, GIF, or WebP).')
        
        return avatar
