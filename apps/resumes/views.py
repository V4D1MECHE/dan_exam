from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Avg, Max
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Resume, ResumeTemplate, WorkExperience, Skill


def resume_list(request):
    """Список резюме с фильтрацией, исключением и сортировкой"""
    resumes = Resume.objects.filter(is_public=True, is_active=True)
    
    # Фильтрация по городу (использование filter)
    city = request.GET.get('city')
    if city:
        resumes = resumes.filter(city__icontains=city)
    
    # Фильтрация по типу занятости
    employment_type = request.GET.get('employment_type')
    if employment_type:
        resumes = resumes.filter(employment_type=employment_type)
    
    # Исключение резюме без фото (использование exclude)
    exclude_no_photo = request.GET.get('exclude_no_photo')
    if exclude_no_photo == '1':
        resumes = resumes.exclude(photo='')
    
    # Поиск по связанной модели через __ (двойное подчеркивание)
    search_query = request.GET.get('search')
    if search_query:
        resumes = resumes.filter(
            user__first_name__icontains=search_query
        ) | resumes.filter(
            user__last_name__icontains=search_query
        ) | resumes.filter(title__icontains=search_query)
    
    # Сортировка (использование order_by)
    sort_by = request.GET.get('sort', '-updated_at')
    if sort_by == 'salary':
        resumes = resumes.order_by('-salary_from')
    elif sort_by == 'date':
        resumes = resumes.order_by('-created_at')
    elif sort_by == 'name':
        resumes = resumes.order_by('user__last_name', 'user__first_name')
    else:
        resumes = resumes.order_by('-updated_at')
    
    # Пагинация с обработкой исключений
    paginator = Paginator(resumes, 10)
    page = request.GET.get('page')
    
    try:
        resumes_page = paginator.page(page)
    except PageNotAnInteger:
        resumes_page = paginator.page(1)
    except EmptyPage:
        resumes_page = paginator.page(paginator.num_pages)
    
    # Статистика с использованием агрегации
    stats = Resume.objects.filter(is_public=True, is_active=True).aggregate(
        total_count=Count('id'),
        avg_salary=Avg('salary_from'),
        max_salary=Max('salary_from')
    )
    
    context = {
        'resumes': resumes_page,
        'stats': stats,
        'city': city,
        'employment_type': employment_type,
        'exclude_no_photo': exclude_no_photo,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'resumes/resume_list.html', context)


def resume_detail(request, pk):
    """Детальный просмотр резюме"""
    resume = get_object_or_404(Resume, pk=pk, is_public=True, is_active=True)
    
    # Использование двойного подчеркивания для связанных моделей
    work_experiences = WorkExperience.objects.filter(
        resume=resume
    ).select_related('resume__user')
    
    context = {
        'resume': resume,
        'work_experiences': work_experiences,
    }
    
    return render(request, 'resumes/resume_detail.html', context)


@login_required
def my_resumes(request):
    """Мои резюме (только для авторизованных пользователей)"""
    # Использование собственного менеджера
    public_resumes = Resume.public_resumes.filter(user=request.user)
    all_resumes = Resume.objects.filter(user=request.user)
    
    # Фильтрация по навыкам через связанную таблицу (__) 
    skill_filter = request.GET.get('skill')
    if skill_filter:
        all_resumes = all_resumes.filter(skills__name__icontains=skill_filter).distinct()
    
    context = {
        'public_resumes': public_resumes,
        'all_resumes': all_resumes,
        'skill_filter': skill_filter,
    }
    
    return render(request, 'resumes/my_resumes.html', context)


def template_list(request):
    """Список шаблонов резюме"""
    templates = ResumeTemplate.objects.filter(is_active=True)
    
    # Исключение шаблонов без превью
    if request.GET.get('with_preview') == '1':
        templates = templates.exclude(preview_image='')
    
    # Сортировка по умолчанию сначала
    templates = templates.order_by('-is_default', 'name')
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'resumes/template_list.html', context)


def resumes_by_year(request, year):
    """Резюме по году создания (демонстрация регулярных выражений в URLs)"""
    resumes = Resume.objects.filter(
        created_at__year=year,
        is_public=True,
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'resumes': resumes,
        'year': year,
    }
    
    return render(request, 'resumes/resumes_by_year.html', context)