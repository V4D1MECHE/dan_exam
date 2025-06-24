from django import template
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from ..models import Resume, Skill, ResumeTemplate

register = template.Library()


@register.simple_tag
def total_resumes():
    """Простой шаблонный тег - возвращает общее количество резюме"""
    return Resume.objects.filter(is_public=True, is_active=True).count()


@register.simple_tag(takes_context=True)
def user_resume_count(context):
    """Шаблонный тег с контекстными переменными - количество резюме пользователя"""
    user = context.get('user')
    if user and user.is_authenticated:
        return Resume.objects.filter(user=user).count()
    return 0


@register.inclusion_tag('resumes/tags/popular_skills.html')
def popular_skills(limit=5):
    """Шаблонный тег, возвращающий набор запросов - популярные навыки"""
    skills = Skill.objects.values('name').annotate(
        usage_count=Count('resume')
    ).order_by('-usage_count')[:limit]
    
    return {'skills': skills}


@register.inclusion_tag('resumes/tags/recent_resumes.html')
def recent_resumes(limit=3):
    """Шаблонный тег, возвращающий последние резюме"""
    resumes = Resume.public_resumes.all()[:limit]
    return {'resumes': resumes}


@register.filter
def salary_format(value):
    """Шаблонный фильтр для форматирования зарплаты"""
    if not value:
        return "Не указана"
    
    # Преобразуем в int для корректного форматирования
    value = int(value)
    
    # Добавим символ валюты в зависимости от того, что передано
    symbol = '₽'  # по умолчанию рубли
    
    if value >= 1000000:
        return f"{value // 1000000}.{(value % 1000000) // 100000} млн {symbol}"
    elif value >= 1000:
        return f"{value // 1000} {value % 1000:03d} {symbol}"
    else:
        return f"{value} {symbol}"


@register.filter
def salary_format_with_currency(value, currency='RUB'):
    """Шаблонный фильтр для форматирования зарплаты с учетом валюты"""
    if not value:
        return "Не указана"
    
    # Преобразуем в int для корректного форматирования
    value = int(value)
    
    # Символы валют
    currency_symbols = {
        'RUB': '₽',
        'USD': '$',
        'EUR': '€',
    }
    symbol = currency_symbols.get(currency, '₽')
    
    if value >= 1000000:
        return f"{value // 1000000}.{(value % 1000000) // 100000} млн {symbol}"
    elif value >= 1000:
        return f"{value // 1000} {value % 1000:03d} {symbol}"
    else:
        return f"{value} {symbol}"


@register.filter
def employment_type_icon(value):
    """Шаблонный фильтр для иконок типа занятости"""
    icons = {
        'FULL': '👔',
        'PART': '⏰',
        'REMOTE': '🏠',
        'HYBRID': '🔄',
    }
    return icons.get(value, '💼')


@register.filter
def public_resumes_count(resumes):
    """Подсчет публичных резюме"""
    if hasattr(resumes, 'filter'):
        return resumes.filter(is_public=True).count()
    return len([r for r in resumes if r.is_public])


@register.filter
def private_resumes_count(resumes):
    """Подсчет приватных резюме"""
    if hasattr(resumes, 'filter'):
        return resumes.filter(is_public=False).count()
    return len([r for r in resumes if not r.is_public])


@register.filter
def recent_resumes_count(resumes):
    """Подсчет резюме, обновленных за последнюю неделю"""
    week_ago = timezone.now() - timedelta(days=7)
    if hasattr(resumes, 'filter'):
        return resumes.filter(updated_at__gte=week_ago).count()
    return len([r for r in resumes if r.updated_at >= week_ago])