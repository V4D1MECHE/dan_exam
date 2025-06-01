from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'middle_name', 'phone', 'birth_date')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванович'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы Bootstrap к полям паролей
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get('email')
        if email:
            # Проверяем, что email уникален
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_phone(self):
        """Валидация телефона"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Убираем все символы кроме цифр
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                raise ValidationError('Введите корректный номер телефона')
        return phone
    
    def save(self, commit=True):
        """Переопределенный метод save с параметром commit"""
        user = super().save(commit=False)
        # Дополнительная обработка перед сохранением
        if self.cleaned_data.get('phone'):
            # Форматируем телефон
            phone_digits = re.sub(r'\D', '', self.cleaned_data['phone'])
            if phone_digits.startswith('7') and len(phone_digits) == 11:
                user.phone = f"+7 ({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:9]}-{phone_digits[9:11]}"
            else:
                user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
        
        return user


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования профиля пользователя"""
    password = None  # Убираем поле пароля из формы редактирования
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'middle_name', 'phone', 'birth_date')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': True  # Email нельзя менять
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def clean_birth_date(self):
        """Валидация даты рождения"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            from datetime import date
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 14:
                raise ValidationError('Вы должны быть старше 14 лет')
            if age > 100:
                raise ValidationError('Проверьте правильность введенной даты')
        return birth_date
    
    def save(self, commit=True):
        """Сохранение с логированием изменений"""
        user = super().save(commit=False)
        
        if commit:
            # Можно добавить логирование изменений профиля
            user.save()
            
        return user