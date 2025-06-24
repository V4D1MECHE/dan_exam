"""
Фильтры для API резюме
"""

import django_filters
from django.db import models
from .models import Resume, Skill, WorkExperience, Education, Contact, Language, Certificate, Award


class ResumeFilter(django_filters.FilterSet):
    """Фильтры для модели Resume"""
    
    # Фильтрация по городу (частичное совпадение)
    city = django_filters.CharFilter(
        field_name='city', 
        lookup_expr='icontains',
        label='Город'
    )
    
    # Фильтрация по типу занятости
    employment_type = django_filters.ChoiceFilter(
        field_name='employment_type',
        choices=Resume.EMPLOYMENT_CHOICES,
        label='Тип занятости'
    )
    
    # Фильтрация по валюте
    currency = django_filters.ChoiceFilter(
        field_name='currency',
        choices=Resume.CURRENCY_CHOICES,
        label='Валюта'
    )
    
    # Диапазон зарплаты
    salary_from_min = django_filters.NumberFilter(
        field_name='salary_from',
        lookup_expr='gte',
        label='Зарплата от (минимум)'
    )
    
    salary_from_max = django_filters.NumberFilter(
        field_name='salary_from',
        lookup_expr='lte',
        label='Зарплата от (максимум)'
    )
    
    salary_to_min = django_filters.NumberFilter(
        field_name='salary_to',
        lookup_expr='gte',
        label='Зарплата до (минимум)'
    )
    
    salary_to_max = django_filters.NumberFilter(
        field_name='salary_to',
        lookup_expr='lte',
        label='Зарплата до (максимум)'
    )
    
    # Фильтрация по наличию фото
    has_photo = django_filters.BooleanFilter(
        method='filter_has_photo',
        label='Есть фото'
    )
    
    # Фильтрация по ключевым навыкам
    has_key_skills = django_filters.BooleanFilter(
        method='filter_has_key_skills',
        label='Есть ключевые навыки'
    )
    
    # Фильтрация по конкретным навыкам
    skills = django_filters.CharFilter(
        method='filter_by_skills',
        label='Навыки (через запятую)'
    )
    
    # Фильтрация по пользователю (имя или фамилия)
    user_name = django_filters.CharFilter(
        method='filter_by_user_name',
        label='Имя пользователя'
    )
    
    # Фильтрация по дате создания
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Создано после'
    )
    
    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Создано до'
    )
    
    # Фильтрация по активности
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Активное'
    )
    
    # Фильтрация по публичности
    is_public = django_filters.BooleanFilter(
        field_name='is_public',
        label='Публичное'
    )

    class Meta:
        model = Resume
        fields = {
            'title': ['icontains', 'exact'],
            'summary': ['icontains'],
        }

    def filter_has_photo(self, queryset, name, value):
        """Фильтр по наличию фото"""
        if value is True:
            return queryset.exclude(photo='')
        elif value is False:
            return queryset.filter(photo='')
        return queryset

    def filter_has_key_skills(self, queryset, name, value):
        """Фильтр по наличию ключевых навыков"""
        if value is True:
            return queryset.filter(skills__is_key_skill=True).distinct()
        elif value is False:
            return queryset.exclude(skills__is_key_skill=True).distinct()
        return queryset

    def filter_by_skills(self, queryset, name, value):
        """Фильтр по списку навыков (через запятую)"""
        if value:
            skills_list = [skill.strip() for skill in value.split(',')]
            return queryset.filter(skills__name__in=skills_list).distinct()
        return queryset

    def filter_by_user_name(self, queryset, name, value):
        """Фильтр по имени или фамилии пользователя"""
        if value:
            return queryset.filter(
                models.Q(user__first_name__icontains=value) |
                models.Q(user__last_name__icontains=value)
            ).distinct()
        return queryset


class SkillFilter(django_filters.FilterSet):
    """Фильтры для модели Skill"""
    
    category = django_filters.ChoiceFilter(
        field_name='category',
        choices=Skill.CATEGORY_CHOICES,
        label='Категория'
    )
    
    level = django_filters.ChoiceFilter(
        field_name='level',
        choices=Skill.LEVEL_CHOICES,
        label='Уровень'
    )
    
    is_key_skill = django_filters.BooleanFilter(
        field_name='is_key_skill',
        label='Ключевой навык'
    )
    
    resume_user = django_filters.CharFilter(
        field_name='resume__user__email',
        lookup_expr='icontains',
        label='Email пользователя'
    )

    class Meta:
        model = Skill
        fields = {
            'name': ['icontains', 'exact'],
            'color': ['exact'],
        }


class WorkExperienceFilter(django_filters.FilterSet):
    """Фильтры для модели WorkExperience"""
    
    is_current = django_filters.BooleanFilter(
        field_name='is_current',
        label='Текущая работа'
    )
    
    start_date_after = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Начал работать после'
    )
    
    start_date_before = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        label='Начал работать до'
    )
    
    resume_user = django_filters.CharFilter(
        field_name='resume__user__email',
        lookup_expr='icontains',
        label='Email пользователя'
    )

    class Meta:
        model = WorkExperience
        fields = {
            'company_name': ['icontains', 'exact'],
            'position': ['icontains', 'exact'],
        }


class EducationFilter(django_filters.FilterSet):
    """Фильтры для модели Education"""
    
    degree = django_filters.ChoiceFilter(
        field_name='degree',
        choices=Education.DEGREE_CHOICES,
        label='Степень'
    )
    
    is_current = django_filters.BooleanFilter(
        field_name='is_current',
        label='Учится сейчас'
    )
    
    start_date_after = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Начал учиться после'
    )

    class Meta:
        model = Education
        fields = {
            'institution_name': ['icontains', 'exact'],
            'field_of_study': ['icontains', 'exact'],
            'faculty': ['icontains'],
        }


class ContactFilter(django_filters.FilterSet):
    """Фильтры для модели Contact"""
    
    contact_type = django_filters.ChoiceFilter(
        field_name='contact_type',
        choices=Contact.CONTACT_TYPE_CHOICES,
        label='Тип контакта'
    )
    
    is_primary = django_filters.BooleanFilter(
        field_name='is_primary',
        label='Основной контакт'
    )
    
    is_visible = django_filters.BooleanFilter(
        field_name='is_visible',
        label='Видимый'
    )

    class Meta:
        model = Contact
        fields = {
            'value': ['icontains', 'exact'],
            'label': ['icontains'],
        }


class LanguageFilter(django_filters.FilterSet):
    """Фильтры для модели Language"""
    
    level = django_filters.ChoiceFilter(
        field_name='level',
        choices=Language.LEVEL_CHOICES,
        label='Уровень'
    )
    
    is_native = django_filters.BooleanFilter(
        field_name='is_native',
        label='Родной язык'
    )

    class Meta:
        model = Language
        fields = {
            'name': ['icontains', 'exact'],
        }


class CertificateFilter(django_filters.FilterSet):
    """Фильтры для модели Certificate"""
    
    issue_date_after = django_filters.DateFilter(
        field_name='issue_date',
        lookup_expr='gte',
        label='Выдан после'
    )
    
    issue_date_before = django_filters.DateFilter(
        field_name='issue_date',
        lookup_expr='lte',
        label='Выдан до'
    )
    
    has_expiry = django_filters.BooleanFilter(
        method='filter_has_expiry',
        label='Есть срок истечения'
    )
    
    is_expired = django_filters.BooleanFilter(
        method='filter_is_expired',
        label='Истёк'
    )

    class Meta:
        model = Certificate
        fields = {
            'name': ['icontains', 'exact'],
            'issuer': ['icontains', 'exact'],
            'credential_id': ['exact'],
        }

    def filter_has_expiry(self, queryset, name, value):
        """Фильтр по наличию срока истечения"""
        if value is True:
            return queryset.exclude(expiry_date__isnull=True)
        elif value is False:
            return queryset.filter(expiry_date__isnull=True)
        return queryset

    def filter_is_expired(self, queryset, name, value):
        """Фильтр по истёкшим сертификатам"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value is True:
            return queryset.filter(expiry_date__lt=today)
        elif value is False:
            return queryset.filter(
                models.Q(expiry_date__gte=today) | 
                models.Q(expiry_date__isnull=True)
            )
        return queryset


class AwardFilter(django_filters.FilterSet):
    """Фильтры для модели Award"""
    
    date_after = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='Получена после'
    )
    
    date_before = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='Получена до'
    )

    class Meta:
        model = Award
        fields = {
            'title': ['icontains', 'exact'],
            'issuer': ['icontains', 'exact'],
        }