from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Avg, Max, Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Resume, ResumeTemplate, WorkExperience, Skill, Contact, Education, SkillTag, SkillTagRelation
from .forms import ResumeForm, SkillForm, WorkExperienceForm, EducationForm, ContactForm, SkillTagForm


def resume_list(request):
    """Список резюме с фильтрацией, исключением и сортировкой"""
    # Использование select_related для оптимизации запросов к связанным моделям
    resumes = Resume.objects.filter(is_public=True, is_active=True).select_related(
        'user', 'template'
    ).prefetch_related(
        # Использование prefetch_related для оптимизации many-to-many и reverse foreign key
        'skills__tags',
        'work_experiences',
        'contacts'
    )
    
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


# CRUD операции для резюме
class ResumeCreateView(LoginRequiredMixin, CreateView):
    """Создание резюме"""
    model = Resume
    form_class = ResumeForm
    template_name = 'resumes/resume_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Резюме успешно создано!')
        return super().form_valid(form)


class ResumeUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование резюме"""
    model = Resume
    form_class = ResumeForm
    template_name = 'resumes/resume_form.html'
    
    def get_queryset(self):
        # Пользователь может редактировать только свои резюме
        return Resume.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Резюме успешно обновлено!')
        return super().form_valid(form)


class ResumeDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление резюме"""
    model = Resume
    template_name = 'resumes/resume_confirm_delete.html'
    success_url = reverse_lazy('my_resumes')
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Резюме успешно удалено!')
        return super().delete(request, *args, **kwargs)


# CRUD для навыков
@login_required
def skill_create(request, resume_pk):
    """Создание навыка для резюме"""
    resume = get_object_or_404(Resume, pk=resume_pk, user=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.resume = resume
            skill.save()
            form.save_m2m()  # Сохраняем теги
            messages.success(request, 'Навык успешно добавлен!')
            return redirect('resume_detail', pk=resume.pk)
    else:
        form = SkillForm()
    
    context = {
        'form': form,
        'resume': resume,
    }
    return render(request, 'resumes/skill_form.html', context)


@login_required
def skill_update(request, pk):
    """Редактирование навыка"""
    skill = get_object_or_404(Skill, pk=pk, resume__user=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Навык успешно обновлен!')
            return redirect('resume_detail', pk=skill.resume.pk)
    else:
        # Предварительно выбираем связанные теги
        initial_tags = skill.tags.all()
        form = SkillForm(instance=skill, initial={'tags': initial_tags})
    
    context = {
        'form': form,
        'skill': skill,
        'resume': skill.resume,
    }
    return render(request, 'resumes/skill_form.html', context)


@login_required
def skill_delete(request, pk):
    """Удаление навыка"""
    skill = get_object_or_404(Skill, pk=pk, resume__user=request.user)
    resume_pk = skill.resume.pk
    
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Навык успешно удален!')
        return redirect('resume_detail', pk=resume_pk)
    
    context = {
        'skill': skill,
        'resume': skill.resume,
    }
    return render(request, 'resumes/skill_confirm_delete.html', context)


# Views с оптимизированными запросами
class OptimizedResumeListView(ListView):
    """Оптимизированный список резюме с использованием select_related и prefetch_related"""
    model = Resume
    template_name = 'resumes/optimized_resume_list.html'
    context_object_name = 'resumes'
    paginate_by = 20
    
    def get_queryset(self):
        # Демонстрация select_related для ForeignKey
        queryset = Resume.objects.filter(
            is_public=True, 
            is_active=True
        ).select_related(
            'user',  # Избегаем дополнительных запросов для user
            'template'  # Избегаем дополнительных запросов для template
        )
        
        # Демонстрация prefetch_related для reverse ForeignKey и ManyToMany
        queryset = queryset.prefetch_related(
            # Предзагружаем связанные объекты
            'skills',  # Навыки
            'work_experiences',  # Опыт работы
            'educations',  # Образование
            'contacts',  # Контакты
            # Вложенная предзагрузка для many-to-many через промежуточную модель
            Prefetch(
                'skills',
                queryset=Skill.objects.select_related('resume').prefetch_related(
                    'tags',  # Теги навыков
                    'skilltag_set'  # Промежуточная модель
                )
            )
        )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем статистику с агрегацией
        context['stats'] = Resume.objects.filter(
            is_public=True,
            is_active=True
        ).aggregate(
            total_count=Count('id'),
            avg_skills=Avg('skills__level'),
            max_salary=Max('salary_from')
        )
        return context


@login_required
def resume_detail_optimized(request, pk):
    """Оптимизированный детальный просмотр резюме"""
    # Используем select_related для связанных объектов один-к-одному и один-ко-многим
    resume = get_object_or_404(
        Resume.objects.select_related(
            'user',
            'template'
        ).prefetch_related(
            # Используем prefetch_related для обратных связей и many-to-many
            'skills__tags',  # Навыки и их теги
            'work_experiences',  # Опыт работы
            'educations',  # Образование
            'languages',  # Языки
            'awards',  # Награды
            'certificates',  # Сертификаты
            'recommendations',  # Рекомендации
            'contacts',  # Контакты
            # Оптимизированная загрузка навыков с их связями
            Prefetch(
                'skills',
                queryset=Skill.objects.prefetch_related(
                    Prefetch(
                        'skilltag_set',
                        queryset=SkillTagRelation.objects.select_related('tag')
                    )
                )
            )
        ),
        pk=pk,
        user=request.user
    )
    
    context = {
        'resume': resume,
        # Все связанные данные уже загружены, дополнительных запросов не будет
    }
    
    return render(request, 'resumes/resume_detail_optimized.html', context)


# CRUD для других моделей
class WorkExperienceCreateView(LoginRequiredMixin, CreateView):
    """Создание опыта работы"""
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'resumes/work_experience_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.resume = get_object_or_404(Resume, pk=kwargs['resume_pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.resume = self.resume
        messages.success(self.request, 'Опыт работы успешно добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('resume_detail', kwargs={'pk': self.resume.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resume'] = self.resume
        return context


class EducationCreateView(LoginRequiredMixin, CreateView):
    """Создание образования"""
    model = Education
    form_class = EducationForm
    template_name = 'resumes/education_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.resume = get_object_or_404(Resume, pk=kwargs['resume_pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.resume = self.resume
        messages.success(self.request, 'Образование успешно добавлено!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('resume_detail', kwargs={'pk': self.resume.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resume'] = self.resume
        return context


class ContactCreateView(LoginRequiredMixin, CreateView):
    """Создание контакта"""
    model = Contact
    form_class = ContactForm
    template_name = 'resumes/contact_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.resume = get_object_or_404(Resume, pk=kwargs['resume_pk'], user=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.resume = self.resume
        messages.success(self.request, 'Контакт успешно добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('resume_detail', kwargs={'pk': self.resume.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resume'] = self.resume
        return context


# Управление тегами навыков
class SkillTagListView(ListView):
    """Список тегов навыков"""
    model = SkillTag
    template_name = 'resumes/skilltag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        # Предзагружаем связанные навыки для подсчета
        return SkillTag.objects.prefetch_related('skills').annotate(
            skill_count=Count('skills')
        ).order_by('name')


class SkillTagCreateView(CreateView):
    """Создание тега навыка"""
    model = SkillTag
    form_class = SkillTagForm
    template_name = 'resumes/skilltag_form.html'
    success_url = reverse_lazy('skilltag_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Тег успешно создан!')
        return super().form_valid(form)