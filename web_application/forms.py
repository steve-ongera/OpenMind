from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, UserProfile, MoodEntry, ChatMessage


class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a strong password'
        }),
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        }),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 
                  'date_of_birth', 'gender', 'country', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your.email@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your country'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1234567890'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match')
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered')
        return email


class UserLoginForm(forms.Form):
    """User login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """Profile update form"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'university', 'field_of_study', 'academic_year']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Tell us a bit about yourself...'
            }),
            'university': forms.TextInput(attrs={'class': 'form-input'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-input'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-input'}),
        }


class MoodEntryForm(forms.ModelForm):
    """Mood entry form"""
    class Meta:
        model = MoodEntry
        fields = ['mood_level', 'mood_score', 'emotions', 'energy_level', 
                  'sleep_quality', 'sleep_hours', 'activities', 'triggers', 'notes']
        widgets = {
            'mood_level': forms.Select(attrs={'class': 'form-select'}),
            'mood_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 10
            }),
            'emotions': forms.CheckboxSelectMultiple(),
            'energy_level': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 10
            }),
            'sleep_quality': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 10
            }),
            'sleep_hours': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': 0.5
            }),
            'activities': forms.CheckboxSelectMultiple(),
            'triggers': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'What triggered your mood today?'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Additional notes about your day...'
            }),
        }


class ChatMessageForm(forms.ModelForm):
    """Chat message form"""
    class Meta:
        model = ChatMessage
        fields = ['message_text']
        widgets = {
            'message_text': forms.Textarea(attrs={
                'class': 'chat-input',
                'rows': 3,
                'placeholder': 'Type your message here...'
            })
        }