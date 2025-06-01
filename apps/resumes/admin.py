from django.contrib import admin
from django.utils import timezone
from .models import (
    ResumeTemplate, Resume, Contact, WorkExperience, Education,
    Skill, Language, Award, Certificate, Recommendation, SharedLink
)


@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_default', 'get_usage_count', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    list_display_links = ['name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    @admin.display(description='Использований')
    def get_usage_count(self, obj):
        return obj.resume_set.count()
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'preview_image')
        }),
        ('Настройки', {
            'fields': ('is_active', 'is_default')
        }),
        ('Стили', {
            'fields': ('css_styles',),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['get_contact_display', 'resume', 'contact_type', 'is_primary', 'is_visible', 'order']
    list_filter = ['contact_type', 'is_primary', 'is_visible', 'created_at']
    search_fields = ['value', 'label', 'resume__title', 'resume__user__email']
    list_display_links = ['get_contact_display', 'resume']
    raw_id_fields = ['resume']
    
    @admin.display(description='Контакт')
    def get_contact_display(self, obj):
        return f"{obj.get_contact_type_display()}: {obj.value}"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'contact_type', 'value', 'label')
        }),
        ('Настройки отображения', {
            'fields': ('is_primary', 'is_visible', 'order')
        }),
    )


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ['contact_type', 'value', 'label', 'is_primary', 'is_visible', 'order']


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = ['company_name', 'position', 'start_date', 'end_date', 'is_current', 'order']


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    fields = ['institution_name', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current']


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ['name', 'category', 'level', 'is_key_skill', 'order']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'template', 'city', 'employment_type', 'get_salary_range', 'is_public', 'is_active', 'created_at']
    list_filter = ['employment_type', 'currency', 'is_public', 'is_active', 'created_at', 'template']
    search_fields = ['title', 'user__email', 'user__first_name', 'user__last_name', 'city', 'summary']
    list_display_links = ['title', 'user']
    raw_id_fields = ['user', 'template']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    inlines = [ContactInline, WorkExperienceInline, EducationInline, SkillInline]
    
    @admin.display(description='Зарплатная вилка')
    def get_salary_range(self, obj):
        if obj.salary_from and obj.salary_to:
            return f"{obj.salary_from:,} - {obj.salary_to:,} {obj.currency}"
        elif obj.salary_from:
            return f"от {obj.salary_from:,} {obj.currency}"
        elif obj.salary_to:
            return f"до {obj.salary_to:,} {obj.currency}"
        return "Не указана"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'template', 'title', 'photo', 'city')
        }),
        ('Занятость и зарплата', {
            'fields': ('employment_type', 'salary_from', 'salary_to', 'currency')
        }),
        ('Описание', {
            'fields': ('summary',)
        }),
        ('Настройки', {
            'fields': ('is_public', 'is_active')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'position', 'resume', 'start_date', 'end_date', 'is_current', 'get_duration']
    list_filter = ['is_current', 'start_date', 'resume__user']
    search_fields = ['company_name', 'position', 'resume__title', 'resume__user__email']
    list_display_links = ['company_name', 'position']
    raw_id_fields = ['resume']
    date_hierarchy = 'start_date'
    
    @admin.display(description='Длительность работы')
    def get_duration(self, obj):
        end = obj.end_date or timezone.now().date()
        duration = end - obj.start_date
        years = duration.days // 365
        months = (duration.days % 365) // 30
        return f"{years} лет {months} мес."
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'company_name', 'position')
        }),
        ('Период работы', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Описание', {
            'fields': ('description', 'achievements')
        }),
        ('Настройки', {
            'fields': ('order',)
        }),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution_name', 'field_of_study', 'degree', 'resume', 'start_date', 'end_date', 'is_current']
    list_filter = ['degree', 'is_current', 'start_date']
    search_fields = ['institution_name', 'field_of_study', 'faculty', 'resume__title', 'resume__user__email']
    list_display_links = ['institution_name', 'field_of_study']
    raw_id_fields = ['resume']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'institution_name', 'faculty', 'degree', 'field_of_study')
        }),
        ('Период обучения', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Дополнительно', {
            'fields': ('description', 'order')
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'resume', 'is_key_skill', 'order']
    list_filter = ['category', 'level', 'is_key_skill']
    search_fields = ['name', 'resume__title', 'resume__user__email']
    list_display_links = ['name']
    raw_id_fields = ['resume']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'name', 'category', 'level')
        }),
        ('Настройки', {
            'fields': ('is_key_skill', 'order')
        }),
    )


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'resume', 'is_native', 'order']
    list_filter = ['level', 'is_native']
    search_fields = ['name', 'resume__title', 'resume__user__email']
    list_display_links = ['name']
    raw_id_fields = ['resume']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'name', 'level', 'is_native')
        }),
        ('Настройки', {
            'fields': ('order',)
        }),
    )


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['title', 'issuer', 'date', 'resume', 'order']
    list_filter = ['date']
    search_fields = ['title', 'issuer', 'resume__title', 'resume__user__email']
    list_display_links = ['title']
    raw_id_fields = ['resume']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'title', 'issuer', 'date')
        }),
        ('Дополнительно', {
            'fields': ('description', 'order')
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuer', 'issue_date', 'expiry_date', 'resume', 'order']
    list_filter = ['issue_date', 'expiry_date']
    search_fields = ['name', 'issuer', 'credential_id', 'resume__title', 'resume__user__email']
    list_display_links = ['name']
    raw_id_fields = ['resume']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'name', 'issuer')
        }),
        ('Даты', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Данные сертификата', {
            'fields': ('credential_id', 'credential_url')
        }),
        ('Дополнительно', {
            'fields': ('description', 'order')
        }),
    )


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['recommender_name', 'recommender_position', 'recommender_company', 'resume', 'is_visible', 'order']
    list_filter = ['is_visible', 'created_at']
    search_fields = ['recommender_name', 'recommender_company', 'resume__title', 'resume__user__email']
    list_display_links = ['recommender_name']
    raw_id_fields = ['resume']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'recommender_name', 'recommender_position', 'recommender_company')
        }),
        ('Контакты рекомендателя', {
            'fields': ('recommender_phone', 'recommender_email')
        }),
        ('Дополнительно', {
            'fields': ('relationship', 'text')
        }),
        ('Настройки', {
            'fields': ('is_visible', 'order')
        }),
    )


@admin.register(SharedLink)
class SharedLinkAdmin(admin.ModelAdmin):
    list_display = ['slug', 'resume', 'link_type', 'views_count', 'is_active', 'expires_at', 'created_at']
    list_filter = ['link_type', 'is_active', 'created_at', 'expires_at']
    search_fields = ['slug', 'resume__title', 'resume__user__email']
    list_display_links = ['slug', 'resume']
    raw_id_fields = ['resume']
    readonly_fields = ['views_count', 'last_viewed_at', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('resume', 'slug', 'link_type')
        }),
        ('Безопасность', {
            'fields': ('password', 'is_active', 'expires_at')
        }),
        ('Статистика', {
            'fields': ('views_count', 'last_viewed_at')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )