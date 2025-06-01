from django import forms
from django.core.exceptions import ValidationError
from .models import Resume, Skill, WorkExperience, Education, Contact, SkillTag, SkillTagRelation
import re


class ResumeForm(forms.ModelForm):
    """Форма для создания и редактирования резюме"""
    
    class Meta:
        model = Resume
        fields = ['title', 'photo', 'city', 'employment_type', 'salary_from', 'salary_to', 
                  'currency', 'summary', 'is_public', 'template']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Python Developer'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Москва'
            }),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'salary_from': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '100000'
            }),
            'salary_to': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '150000'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Расскажите о себе и своем опыте...'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'template': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_title(self):
        """Валидация поля title"""
        title = self.cleaned_data.get('title')
        if title:
            # Проверяем, что в названии нет только цифр
            if title.isdigit():
                raise ValidationError('Название должности не может состоять только из цифр')
            # Проверяем минимальную длину
            if len(title) < 3:
                raise ValidationError('Название должности должно содержать минимум 3 символа')
        return title
    
    def clean_salary_from(self):
        """Валидация минимальной зарплаты"""
        salary = self.cleaned_data.get('salary_from')
        if salary and salary < 0:
            raise ValidationError('Зарплата не может быть отрицательной')
        return salary
    
    def clean(self):
        """Общая валидация формы"""
        cleaned_data = super().clean()
        salary_from = cleaned_data.get('salary_from')
        salary_to = cleaned_data.get('salary_to')
        
        if salary_from and salary_to:
            if salary_from > salary_to:
                raise ValidationError('Минимальная зарплата не может быть больше максимальной')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Переопределенный метод save с параметром commit"""
        resume = super().save(commit=False)
        
        # Добавляем дополнительную логику перед сохранением
        if not resume.summary:
            resume.summary = f"Опытный специалист на позицию {resume.title}"
        
        if commit:
            resume.save()
            self.save_m2m()  # Сохраняем связи many-to-many
        
        return resume


class SkillForm(forms.ModelForm):
    """Форма для добавления навыков"""
    tags = forms.ModelMultipleChoiceField(
        queryset=SkillTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Теги'
    )
    
    class Meta:
        model = Skill
        fields = ['name', 'category', 'level', 'is_key_skill', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'is_key_skill': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        """Валидация названия навыка"""
        name = self.cleaned_data.get('name')
        if name:
            # Убираем лишние пробелы
            name = ' '.join(name.split())
            # Проверяем на спецсимволы
            if not re.match(r'^[\w\s\-\+\#\.]+$', name):
                raise ValidationError('Название навыка содержит недопустимые символы')
        return name
    
    def save(self, commit=True):
        """Сохранение с обработкой тегов"""
        skill = super().save(commit=False)
        
        if commit:
            skill.save()
            # Обрабатываем теги
            if 'tags' in self.cleaned_data:
                skill.tags.clear()
                for tag in self.cleaned_data['tags']:
                    SkillTagRelation.objects.create(
                        skill=skill,
                        tag=tag,
                        relevance=100
                    )
        
        return skill


class WorkExperienceForm(forms.ModelForm):
    """Форма для опыта работы"""
    
    class Meta:
        model = WorkExperience
        fields = ['company_name', 'position', 'start_date', 'end_date', 
                  'is_current', 'description', 'achievements']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ООО "Компания"'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Senior Python Developer'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Основные достижения на данной позиции'
            }),
        }
    
    def clean(self):
        """Валидация дат"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_current = cleaned_data.get('is_current')
        
        if not is_current and start_date and end_date:
            if start_date > end_date:
                raise ValidationError('Дата начала не может быть позже даты окончания')
        
        if is_current and end_date:
            cleaned_data['end_date'] = None
            
        return cleaned_data


class EducationForm(forms.ModelForm):
    """Форма для образования"""
    
    class Meta:
        model = Education
        fields = ['institution_name', 'faculty', 'degree', 'field_of_study',
                  'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'institution_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'МГУ им. М.В. Ломоносова'
            }),
            'faculty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Факультет ВМК'
            }),
            'degree': forms.Select(attrs={'class': 'form-select'}),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Прикладная математика и информатика'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def clean_institution_name(self):
        """Валидация названия учебного заведения"""
        name = self.cleaned_data.get('institution_name')
        if name and len(name) < 3:
            raise ValidationError('Название учебного заведения слишком короткое')
        return name


class ContactForm(forms.ModelForm):
    """Форма для контактов"""
    
    class Meta:
        model = Contact
        fields = ['contact_type', 'value', 'label', 'is_primary', 'is_visible']
        widgets = {
            'contact_type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите контактные данные'
            }),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Подпись (необязательно)'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_value(self):
        """Валидация значения контакта в зависимости от типа"""
        value = self.cleaned_data.get('value')
        contact_type = self.cleaned_data.get('contact_type')
        
        if value and contact_type:
            if contact_type == 'EMAIL':
                # Простая валидация email
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                    raise ValidationError('Введите корректный email адрес')
            elif contact_type == 'PHONE':
                # Валидация телефона
                phone_digits = re.sub(r'\D', '', value)
                if len(phone_digits) < 10 or len(phone_digits) > 15:
                    raise ValidationError('Введите корректный номер телефона')
            elif contact_type in ['WEBSITE', 'LINKEDIN', 'GITHUB']:
                # Валидация URL
                if not value.startswith(('http://', 'https://')):
                    value = 'https://' + value
                    
        return value
    
    def save(self, commit=True):
        """Сохранение с дополнительной обработкой"""
        contact = super().save(commit=False)
        
        # Если это основной контакт, сбрасываем флаг у других контактов того же типа
        if commit and contact.is_primary:
            Contact.objects.filter(
                resume=contact.resume,
                contact_type=contact.contact_type,
                is_primary=True
            ).exclude(pk=contact.pk).update(is_primary=False)
        
        if commit:
            contact.save()
            
        return contact


class SkillTagForm(forms.ModelForm):
    """Форма для тегов навыков"""
    
    class Meta:
        model = SkillTag
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Backend'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
        }
    
    def clean_color(self):
        """Валидация цвета"""
        color = self.cleaned_data.get('color')
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValidationError('Введите корректный цвет в формате #RRGGBB')
        return color