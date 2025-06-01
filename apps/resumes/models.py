from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.db.models import Manager
from django.core.exceptions import ValidationError
import uuid


class PublicResumeManager(Manager):
    """Кастомный менеджер для публичных резюме"""
    def get_queryset(self):
        return super().get_queryset().filter(is_public=True, is_active=True)


class ResumeTemplate(models.Model):
    """Шаблон резюме"""
    name = models.CharField(max_length=100, verbose_name="Название шаблона")
    description = models.TextField(blank=True, verbose_name="Описание")
    preview_image = models.ImageField(upload_to='templates/previews/', blank=True, verbose_name="Превью")
    css_styles = models.JSONField(default=dict, blank=True, verbose_name="CSS стили")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_default = models.BooleanField(default=False, verbose_name="По умолчанию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Шаблон резюме"
        verbose_name_plural = "Шаблоны резюме"
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name


class Resume(models.Model):
    """Резюме"""
    EMPLOYMENT_CHOICES = [
        ('FULL', 'Полная занятость'),
        ('PART', 'Частичная занятость'),
        ('REMOTE', 'Удаленная работа'),
        ('HYBRID', 'Гибридная работа'),
    ]
    
    CURRENCY_CHOICES = [
        ('RUB', 'Рубли'),
        ('USD', 'Доллары'),
        ('EUR', 'Евро'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="resumes")
    template = models.ForeignKey(ResumeTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Шаблон", related_name="resumes")
    title = models.CharField(max_length=200, verbose_name="Должность")
    photo = models.ImageField(upload_to='resumes/photos/', blank=True, verbose_name="Фото")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, blank=True, verbose_name="Тип занятости")
    salary_from = models.PositiveIntegerField(null=True, blank=True, verbose_name="Зарплата от")
    salary_to = models.PositiveIntegerField(null=True, blank=True, verbose_name="Зарплата до")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='RUB', verbose_name="Валюта")
    summary = models.TextField(blank=True, verbose_name="Краткое описание")
    is_public = models.BooleanField(default=False, verbose_name="Публичное")
    is_active = models.BooleanField(default=True, verbose_name="Активное")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    objects = models.Manager()
    public_resumes = PublicResumeManager()
    
    class Meta:
        verbose_name = "Резюме"
        verbose_name_plural = "Резюме"
        ordering = ['-updated_at', '-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('resume_detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        """Переопределенный метод save для демонстрации"""
        # Автоматически делаем резюме публичным если заполнено больше 50% полей
        filled_fields = 0
        total_fields = 6  # title, photo, city, employment_type, salary_from, summary
        
        if self.title:
            filled_fields += 1
        if self.photo:
            filled_fields += 1
        if self.city:
            filled_fields += 1
        if self.employment_type:
            filled_fields += 1
        if self.salary_from:
            filled_fields += 1
        if self.summary:
            filled_fields += 1
            
        if filled_fields >= 4:  # больше 50%
            self.is_public = True
            
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Контакты"""
    CONTACT_TYPE_CHOICES = [
        ('PHONE', 'Телефон'),
        ('EMAIL', 'Email'),
        ('TELEGRAM', 'Telegram'),
        ('LINKEDIN', 'LinkedIn'),
        ('GITHUB', 'GitHub'),
        ('WEBSITE', 'Веб-сайт'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="contacts")
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, verbose_name="Тип контакта")
    value = models.CharField(max_length=255, verbose_name="Значение")
    label = models.CharField(max_length=100, blank=True, verbose_name="Подпись")
    is_primary = models.BooleanField(default=False, verbose_name="Основной")
    is_visible = models.BooleanField(default=True, verbose_name="Видимый")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.get_contact_type_display()}: {self.value}"


class WorkExperience(models.Model):
    """Опыт работы"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="work_experiences")
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    position = models.CharField(max_length=200, verbose_name="Должность")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    is_current = models.BooleanField(default=False, verbose_name="По настоящее время")
    description = models.TextField(blank=True, verbose_name="Описание")
    achievements = models.TextField(blank=True, verbose_name="Достижения")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Опыт работы"
        verbose_name_plural = "Опыт работы"
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.company_name} - {self.position}"
    
    def save(self, *args, **kwargs):
        """Переопределение метода save() для автоматической логики"""
        # Если текущая работа, убираем дату окончания
        if self.is_current:
            self.end_date = None
        
        # Автоматически ставим порядок, если не указан
        if not self.order:
            max_order = WorkExperience.objects.filter(resume=self.resume).aggregate(models.Max('order'))['order__max']
            self.order = (max_order or 0) + 1
        
        # Вызываем родительский save()
        super().save(*args, **kwargs)


class Education(models.Model):
    """Образование"""
    DEGREE_CHOICES = [
        ('SECONDARY', 'Среднее'),
        ('SPECIALIZED_SECONDARY', 'Среднее специальное'),
        ('INCOMPLETE_HIGHER', 'Неоконченное высшее'),
        ('BACHELOR', 'Бакалавр'),
        ('MASTER', 'Магистр'),
        ('PHD', 'Кандидат наук'),
        ('DOCTOR', 'Доктор наук'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="educations")
    institution_name = models.CharField(max_length=200, verbose_name="Учебное заведение")
    faculty = models.CharField(max_length=200, blank=True, verbose_name="Факультет")
    degree = models.CharField(max_length=30, choices=DEGREE_CHOICES, blank=True, verbose_name="Степень")
    field_of_study = models.CharField(max_length=200, blank=True, verbose_name="Специальность")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    is_current = models.BooleanField(default=False, verbose_name="Учусь сейчас")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Образование"
        verbose_name_plural = "Образование"
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.institution_name} - {self.field_of_study}"


class SkillTag(models.Model):
    """Теги навыков для группировки"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")
    description = models.TextField(blank=True, verbose_name="Описание")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Цвет")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Тег навыка"
        verbose_name_plural = "Теги навыков"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SkillTagRelation(models.Model):
    """Промежуточная модель для связи навыков и тегов"""
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE, verbose_name="Навык")
    tag = models.ForeignKey(SkillTag, on_delete=models.CASCADE, verbose_name="Тег")
    relevance = models.IntegerField(default=100, verbose_name="Релевантность")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        verbose_name = "Связь навык-тег"
        verbose_name_plural = "Связи навык-тег"
        unique_together = ['skill', 'tag']
        ordering = ['-relevance']
    
    def __str__(self):
        return f"{self.skill.name} - {self.tag.name} ({self.relevance}%)"


class Skill(models.Model):
    """Навыки"""
    LEVEL_CHOICES = [
        (1, 'Начальный'),
        (2, 'Базовый'),
        (3, 'Средний'),
        (4, 'Продвинутый'),
        (5, 'Эксперт'),
    ]
    
    CATEGORY_CHOICES = [
        ('TECHNICAL', 'Технические'),
        ('SOFT', 'Гибкие'),
        ('LANGUAGE', 'Языковые'),
        ('OTHER', 'Другие'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="skills")
    name = models.CharField(max_length=100, verbose_name="Название")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TECHNICAL', verbose_name="Категория")
    level = models.IntegerField(choices=LEVEL_CHOICES, default=3, verbose_name="Уровень")
    is_key_skill = models.BooleanField(default=False, verbose_name="Ключевой навык")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    tags = models.ManyToManyField(SkillTag, through='SkillTagRelation', related_name='skills', verbose_name="Теги")
    
    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ['-is_key_skill', 'order', 'name']
    
    def __str__(self):
        return self.name


class Language(models.Model):
    """Языки"""
    LEVEL_CHOICES = [
        ('A1', 'A1 - Начальный'),
        ('A2', 'A2 - Элементарный'),
        ('B1', 'B1 - Средний'),
        ('B2', 'B2 - Выше среднего'),
        ('C1', 'C1 - Продвинутый'),
        ('C2', 'C2 - Носитель'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="languages")
    name = models.CharField(max_length=100, verbose_name="Язык")
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name="Уровень")
    is_native = models.BooleanField(default=False, verbose_name="Родной")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Язык"
        verbose_name_plural = "Языки"
        ordering = ['-is_native', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"


class Award(models.Model):
    """Награды и достижения"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="awards")
    title = models.CharField(max_length=200, verbose_name="Название")
    issuer = models.CharField(max_length=200, blank=True, verbose_name="Организация")
    date = models.DateField(verbose_name="Дата получения")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Награда"
        verbose_name_plural = "Награды"
        ordering = ['-date', 'order']
    
    def __str__(self):
        return self.title


class Certificate(models.Model):
    """Сертификаты"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="certificates")
    name = models.CharField(max_length=200, verbose_name="Название")
    issuer = models.CharField(max_length=200, verbose_name="Организация")
    issue_date = models.DateField(verbose_name="Дата выдачи")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Дата истечения")
    credential_id = models.CharField(max_length=100, blank=True, verbose_name="ID сертификата")
    credential_url = models.URLField(blank=True, verbose_name="Ссылка на сертификат")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        ordering = ['-issue_date', 'order']
    
    def __str__(self):
        return f"{self.name} - {self.issuer}"


class Recommendation(models.Model):
    """Рекомендации"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="recommendations")
    recommender_name = models.CharField(max_length=200, verbose_name="ФИО рекомендателя")
    recommender_position = models.CharField(max_length=200, verbose_name="Должность рекомендателя")
    recommender_company = models.CharField(max_length=200, blank=True, verbose_name="Компания рекомендателя")
    recommender_phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон рекомендателя")
    recommender_email = models.EmailField(blank=True, verbose_name="Email рекомендателя")
    relationship = models.CharField(max_length=200, blank=True, verbose_name="Отношение к соискателю")
    text = models.TextField(blank=True, verbose_name="Текст рекомендации")
    is_visible = models.BooleanField(default=True, verbose_name="Показывать в резюме")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.recommender_name} - {self.recommender_position}"


class SharedLink(models.Model):
    """Публичные ссылки на резюме"""
    LINK_TYPE_CHOICES = [
        ('PUBLIC', 'Публичная'),
        ('PROTECTED', 'Защищенная'),
        ('TEMPORARY', 'Временная'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, verbose_name="Резюме", related_name="shared_links")
    slug = models.SlugField(max_length=100, unique=True, default=uuid.uuid4, verbose_name="Уникальный идентификатор")
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='PUBLIC', verbose_name="Тип ссылки")
    password = models.CharField(max_length=128, blank=True, verbose_name="Пароль")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата истечения")
    last_viewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Последний просмотр")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Публичная ссылка"
        verbose_name_plural = "Публичные ссылки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.resume} - {self.slug}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)