from django import forms
from django.core.exceptions import ValidationError
from .models import Resume, Skill, WorkExperience, Education, Contact, Language
import re


class ResumeForm(forms.ModelForm):
    """Форма для создания и редактирования резюме"""
    
    # Пример forms.CharField с виджетом Textarea
    additional_info = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Дополнительная информация...'
        }),
        required=False,
        label='Дополнительная информация',
        help_text='Любая дополнительная информация о вас'
    )
    
    # Поле для быстрого добавления навыков на основе цветовых категорий
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),  # Пустой queryset, будет обновлен в __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Навыки',
        help_text='Выберите навыки для резюме'
    )
    
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Обновляем queryset для skills, чтобы получить актуальный список навыков
        self.fields['skills'].queryset = Skill.objects.all()
    
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
            
            # Создаем навыки на основе выбранных навыков
            selected_skills = self.cleaned_data.get('skills', [])
            for skill_template in selected_skills:
                # Создаем копию навыка для данного резюме
                Skill.objects.create(
                    resume=resume,
                    name=skill_template.name,
                    category=skill_template.category,
                    level=3,  # Средний уровень по умолчанию
                    color=skill_template.color,
                    is_key_skill=True,  # Основные навыки считаем ключевыми
                    order=0
                )
        
        return resume


class SkillForm(forms.ModelForm):
    """Форма для добавления навыков"""
    
    class Meta:
        model = Skill
        fields = ['name', 'category', 'level', 'is_key_skill', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Python, React, SQL'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'is_key_skill': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#007bff'
            }),
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


class LanguageForm(forms.ModelForm):
    """Форма для языков"""
    
    class Meta:
        model = Language
        fields = ['name', 'level', 'is_native']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Английский, Русский'
            }),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'is_native': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        """Валидация названия языка"""
        name = self.cleaned_data.get('name')
        if name:
            # Убираем лишние пробелы и делаем первую букву заглавной
            name = ' '.join(word.capitalize() for word in name.split())
            # Проверяем на валидные символы (только буквы и пробелы)
            if not re.match(r'^[a-zA-Zа-яА-Я\s]+$', name):
                raise ValidationError('Название языка должно содержать только буквы')
        return name




class ResumeSkillsForm(forms.Form):
    """Форма для управления навыками резюме через чекбоксы"""
    
    def __init__(self, *args, **kwargs):
        self.resume = kwargs.pop('resume', None)
        super().__init__(*args, **kwargs)
        
        if self.resume:
            # Получаем все существующие уникальные навыки для выбора
            all_skill_names = Skill.objects.values_list('name', flat=True).distinct()
            current_skill_names = set(
                self.resume.skills.values_list('name', flat=True)
            )
            
            # Создаем поле для каждого уникального навыка
            for skill_name in all_skill_names:
                field_name = f'skill_{skill_name.replace(" ", "_").lower()}'
                # Получаем пример навыка для цвета
                sample_skill = Skill.objects.filter(name=skill_name).first()
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    label=skill_name,
                    initial=skill_name in current_skill_names,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input',
                        'data-skill-name': skill_name,
                        'data-skill-color': sample_skill.color if sample_skill else '#007bff'
                    })
                )
                # Добавляем информацию о навыке в поле для использования в шаблоне
                self.fields[field_name].skill_name = skill_name
                self.fields[field_name].skill_color = sample_skill.color if sample_skill else '#007bff'
    
    def save(self):
        if not self.resume:
            return
        
        # Получаем выбранные навыки
        selected_skill_names = []
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('skill_') and value:
                skill_name = self.fields[field_name].skill_name
                selected_skill_names.append(skill_name)
        
        # Удаляем все существующие навыки
        self.resume.skills.all().delete()
        
        # Создаем новые навыки для выбранных
        for skill_name in selected_skill_names:
            # Получаем образец навыка для копирования параметров
            sample_skill = Skill.objects.filter(name=skill_name).first()
            if sample_skill:
                Skill.objects.create(
                    resume=self.resume,
                    name=skill_name,
                    category=sample_skill.category,
                    level=3,  # Средний уровень по умолчанию
                    color=sample_skill.color,
                    is_key_skill=True,
                    order=0
                )
            else:
                # Создаем новый навык, если образца нет
                Skill.objects.create(
                    resume=self.resume,
                    name=skill_name,
                    category='TECHNICAL',
                    level=3,
                    color='#007bff',
                    is_key_skill=True,
                    order=0
                )