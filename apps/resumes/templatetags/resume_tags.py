from django import template
from django.db.models import Count
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
    if value >= 1000000:
        return f"{value // 1000000}.{(value % 1000000) // 100000} млн ₽"
    elif value >= 1000:
        return f"{value // 1000} {value % 1000:03d} ₽"
    else:
        return f"{value} ₽"


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