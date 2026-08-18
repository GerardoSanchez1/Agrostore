from django import forms
from django.contrib.auth import get_user_model
from .models import ContactRequest, Item

User = get_user_model()


class RegistrationForm(forms.Form):
    """User registration form with email and password confirmation."""
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'tu@correo.com',
            'id': 'register-email',
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'register-password',
        }),
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'register-password-confirm',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        pw2 = cleaned_data.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        return User.objects.create_user(email=email, password=password)


class LoginForm(forms.Form):
    """Login form using email and password."""
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'tu@correo.com',
            'id': 'login-email',
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'login-password',
        }),
    )


class ContactForm(forms.Form):
    """Contact / purchase request form."""
    name = forms.CharField(
        label='Nombre',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu nombre completo',
            'id': 'contact-name',
        }),
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'tu@correo.com',
            'id': 'contact-email',
        }),
    )
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'placeholder': 'Describe los productos que te interesan o tu consulta...',
            'rows': 5,
            'id': 'contact-message',
        }),
    )
    products = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        required=False,
        label='Productos de interés',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'product-checkbox',
        }),
    )


class SearchForm(forms.Form):
    """Search form."""
    q = forms.CharField(
        label='',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Buscar productos, marcas, categorías...',
            'id': 'search-input',
        }),
    )
