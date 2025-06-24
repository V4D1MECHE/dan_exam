from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Avg, Max, Prefetch, Q
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from .models import Resume, ResumeTemplate, WorkExperience, Skill, Contact, Education, Language
from .forms import ResumeForm, SkillForm, WorkExperienceForm, EducationForm, ContactForm, LanguageForm, ResumeSkillsForm


def resume_list(request):
    """Список резюме с фильтрацией, исключением и сортировкой"""
    # Использование select_related для оптимизации запросов к связанным моделям
    resumes = Resume.objects.filter(is_public=True, is_active=True).select_related(
        'user', 'template'
    ).prefetch_related(
        # Использование prefetch_related для оптимизации many-to-many и reverse foreign key
        'skills',
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
    
    # Фильтр только с ключевыми навыками
    key_skills_only = request.GET.get('key_skills_only')
    if key_skills_only == '1':
        resumes = resumes.filter(skills__is_key_skill=True).distinct()
    
    # Расширенный поиск по имени, должности, навыкам и описанию
    search_query = request.GET.get('search')
    if search_query:
        resumes = resumes.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(skills__name__icontains=search_query) |
            Q(summary__icontains=search_query)
        ).distinct()
    
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
    
    # Примеры values() и values_list() для демонстрации
    # values() - возвращает словари с указанными полями
    city_stats = Resume.public_resumes.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # values_list() - возвращает кортежи значений
    recent_titles = Resume.public_resumes.values_list(
        'title', 'created_at'
    ).order_by('-created_at')[:5]
    
    # Примеры count() и exists()
    active_resumes_count = Resume.public_resumes.count()  # count() 
    has_remote_jobs = Resume.public_resumes.filter(
        employment_type='REMOTE'
    ).exists()  # exists()
    
    context = {
        'resumes': resumes_page,
        'stats': stats,
        'city_stats': city_stats,
        'recent_titles': recent_titles,
        'active_resumes_count': active_resumes_count,
        'has_remote_jobs': has_remote_jobs,
        'city': city,
        'employment_type': employment_type,
        'exclude_no_photo': exclude_no_photo,
        'key_skills_only': key_skills_only,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'resumes/resume_list.html', context)


def resume_detail(request, pk):
    """Детальный просмотр резюме"""
    resume = get_object_or_404(Resume, pk=pk, is_public=True, is_active=True)
    
    # Использование сессий Django для подсчета просмотров
    session_key = f'resume_viewed_{pk}'
    if not request.session.get(session_key, False):
        request.session[session_key] = True
        request.session.set_expiry(3600)  # Сессия истекает через час
        # Здесь можно было бы увеличить счетчик просмотров
    
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
    
    # Пагинация
    paginator = Paginator(all_resumes, 6)  # 6 резюме на страницу
    page = request.GET.get('page')
    try:
        resumes = paginator.page(page)
    except PageNotAnInteger:
        resumes = paginator.page(1)
    except EmptyPage:
        resumes = paginator.page(paginator.num_pages)
    
    context = {
        'public_resumes': public_resumes,
        'all_resumes': all_resumes,
        'resumes': resumes,  # Пагинированные резюме
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


# Создаем formsets для контактов и языков
ContactFormSet = inlineformset_factory(
    Resume, Contact, form=ContactForm, 
    fields=['contact_type', 'value', 'label', 'is_primary', 'is_visible'],
    extra=2, can_delete=True
)

LanguageFormSet = inlineformset_factory(
    Resume, Language, form=LanguageForm,
    fields=['name', 'level', 'is_native'],
    extra=2, can_delete=True
)

# CRUD операции для резюме
class ResumeCreateView(LoginRequiredMixin, CreateView):
    """Создание резюме с обработкой файлов и inline формами"""
    model = Resume
    form_class = ResumeForm
    template_name = 'resumes/resume_form.html'
    success_url = reverse_lazy('my_resumes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['contact_formset'] = ContactFormSet(self.request.POST, instance=self.object)
            context['language_formset'] = LanguageFormSet(self.request.POST, instance=self.object)
        else:
            context['contact_formset'] = ContactFormSet(instance=self.object)
            context['language_formset'] = LanguageFormSet(instance=self.object)
        return context
    
    def post(self, request, *args, **kwargs):
        """Переопределяем post для демонстрации request.FILES"""
        # Демонстрация request.FILES
        if 'photo' in request.FILES:
            uploaded_file = request.FILES['photo']
            # Можно добавить дополнительную обработку файла
            if uploaded_file.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, 'Файл слишком большой!')
                return self.form_invalid(None)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        context = self.get_context_data()
        contact_formset = context['contact_formset']
        language_formset = context['language_formset']
        
        if contact_formset.is_valid() and language_formset.is_valid():
            form.instance.user = self.request.user
            self.object = form.save()
            contact_formset.instance = self.object
            language_formset.instance = self.object
            contact_formset.save()
            language_formset.save()
            messages.success(self.request, 'Резюме успешно создано!')
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class ResumeUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование резюме с inline формами"""
    model = Resume
    form_class = ResumeForm
    template_name = 'resumes/resume_form.html'
    
    def get_queryset(self):
        # Пользователь может редактировать только свои резюме
        return Resume.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['contact_formset'] = ContactFormSet(self.request.POST, instance=self.object)
            context['language_formset'] = LanguageFormSet(self.request.POST, instance=self.object)
        else:
            context['contact_formset'] = ContactFormSet(instance=self.object)
            context['language_formset'] = LanguageFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        contact_formset = context['contact_formset']
        language_formset = context['language_formset']
        
        if contact_formset.is_valid() and language_formset.is_valid():
            self.object = form.save()
            contact_formset.instance = self.object
            language_formset.instance = self.object
            contact_formset.save()
            language_formset.save()
            messages.success(self.request, 'Резюме успешно обновлено!')
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


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
            # form.save_m2m()  # Tags no longer exist
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
            
            # Пример использования update() для массового обновления
            # Обновляем порядок всех навыков данного резюме
            Skill.objects.filter(resume=skill.resume).update(
                order=models.F('order') + 1
            )
            
            messages.success(request, 'Навык успешно обновлен!')
            return redirect('resume_detail', pk=skill.resume.pk)
    else:
        # Tags no longer exist, use simple form initialization
        form = SkillForm(instance=skill)
    
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
    """Оптимизированный список резюме с поиском и фильтрацией"""
    model = Resume
    template_name = 'resumes/optimized_resume_list.html'
    context_object_name = 'resumes'
    paginate_by = 20
    
    def get_queryset(self):
        # Базовый queryset с оптимизацией
        queryset = Resume.objects.filter(
            is_public=True, 
            is_active=True
        ).select_related(
            'user',  # Избегаем дополнительных запросов для user
            'template'  # Избегаем дополнительных запросов для template
        ).prefetch_related(
            # Предзагружаем связанные объекты
            'work_experiences',  # Опыт работы
            'educations',  # Образование
            'contacts',  # Контакты
            'skills'  # Навыки
        )
        
        # Фильтрация по городу
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Фильтрация по типу занятости
        employment_type = self.request.GET.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        
        # Исключение резюме без фото
        exclude_no_photo = self.request.GET.get('exclude_no_photo')
        if exclude_no_photo == '1':
            queryset = queryset.exclude(photo='')
        
        # Фильтр только с ключевыми навыками
        key_skills_only = self.request.GET.get('key_skills_only')
        if key_skills_only == '1':
            queryset = queryset.filter(skills__is_key_skill=True).distinct()
        
        # Поиск по имени, должности и навыкам
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(skills__name__icontains=search_query) |
                Q(summary__icontains=search_query)
            ).distinct()
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-updated_at')
        if sort_by == 'salary':
            queryset = queryset.order_by('-salary_from')
        elif sort_by == 'date':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'name':
            queryset = queryset.order_by('user__last_name', 'user__first_name')
        else:
            queryset = queryset.order_by('-updated_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем параметры поиска в контекст для сохранения в форме
        context['search_query'] = self.request.GET.get('search', '')
        context['city'] = self.request.GET.get('city', '')
        context['employment_type'] = self.request.GET.get('employment_type', '')
        context['exclude_no_photo'] = self.request.GET.get('exclude_no_photo', '')
        context['key_skills_only'] = self.request.GET.get('key_skills_only', '')
        context['sort_by'] = self.request.GET.get('sort', '-updated_at')
        
        # Статистика с агрегацией
        context['stats'] = Resume.objects.filter(
            is_public=True,
            is_active=True
        ).aggregate(
            total_count=Count('id'),
            avg_skills=Avg('skills__level'),
            max_salary=Max('salary_from')
        )
        
        return context


def resume_detail_optimized(request, pk):
    """Оптимизированный детальный просмотр резюме"""
    # Используем select_related для связанных объектов один-к-одному и один-ко-многим
    resume = get_object_or_404(
        Resume.objects.select_related(
            'user',
            'template'
        ).prefetch_related(
            # Используем prefetch_related для обратных связей и many-to-many
            'work_experiences',  # Опыт работы
            'educations',  # Образование
            'languages',  # Языки
            'awards',  # Награды
            'certificates',  # Сертификаты
            'recommendations',  # Рекомендации
            'contacts',  # Контакты
            # Загружаем навыки
            'skills'
        ),
        pk=pk,
        is_public=True,
        is_active=True
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
# COMMENTED OUT: SkillTag models no longer exist after skills system simplification
# class SkillTagListView(ListView):
#     """Список тегов навыков"""
#     model = SkillTag
#     template_name = 'resumes/skilltag_list.html'
#     context_object_name = 'tags'
#     
#     def get_queryset(self):
#         # Предзагружаем связанные навыки для подсчета
#         return SkillTag.objects.prefetch_related('skills').annotate(
#             skill_count=Count('skills')
#         ).order_by('name')


# class SkillTagCreateView(CreateView):
#     """Создание тега навыка"""
#     model = SkillTag
#     form_class = SkillTagForm
#     template_name = 'resumes/skilltag_form.html'
#     success_url = reverse_lazy('skilltag_list')
#     
#     def form_valid(self, form):
#         messages.success(self.request, 'Тег успешно создан!')
#         return super().form_valid(form)


# class SkillTagUpdateView(UpdateView):
#     """Редактирование тега навыка"""
#     model = SkillTag
#     form_class = SkillTagForm
#     template_name = 'resumes/skilltag_form.html'
#     success_url = reverse_lazy('skilltag_list')
#     
#     def form_valid(self, form):
#         messages.success(self.request, 'Тег успешно обновлен!')
#         return super().form_valid(form)


# class SkillTagDeleteView(DeleteView):
#     """Удаление тега навыка"""
#     model = SkillTag
#     template_name = 'resumes/skilltag_confirm_delete.html'
#     success_url = reverse_lazy('skilltag_list')
#     
#     def delete(self, request, *args, **kwargs):
#         messages.success(request, 'Тег успешно удален!')
#         return super().delete(request, *args, **kwargs)


@login_required
def manage_resume_skills(request, resume_pk):
    """Управление навыками резюме через чекбоксы"""
    resume = get_object_or_404(Resume, pk=resume_pk, user=request.user)
    
    if request.method == 'POST':
        form = ResumeSkillsForm(request.POST, resume=resume)
        if form.is_valid():
            form.save()
            messages.success(request, 'Навыки резюме успешно обновлены!')
            return redirect('resume_detail_optimized', pk=resume.pk)
    else:
        form = ResumeSkillsForm(resume=resume)
    
    context = {
        'form': form,
        'resume': resume,
    }
    return render(request, 'resumes/manage_skills.html', context)


# CRUD операции для контактов
@login_required
def contact_create(request, resume_pk):
    """Создание контакта для резюме"""
    resume = get_object_or_404(Resume, pk=resume_pk, user=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.resume = resume
            contact.save()
            messages.success(request, 'Контакт успешно добавлен!')
            return redirect('resume_detail', pk=resume.pk)
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'resume': resume,
        'title': 'Добавить контакт'
    }
    
    return render(request, 'resumes/contact_form.html', context)


@login_required
def contact_update(request, pk):
    """Редактирование контакта"""
    contact = get_object_or_404(Contact, pk=pk, resume__user=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Контакт успешно обновлен!')
            return redirect('resume_detail', pk=contact.resume.pk)
    else:
        form = ContactForm(instance=contact)
    
    context = {
        'form': form,
        'contact': contact,
        'resume': contact.resume,
        'title': 'Редактировать контакт'
    }
    
    return render(request, 'resumes/contact_form.html', context)


@login_required
def contact_delete(request, pk):
    """Удаление контакта"""
    contact = get_object_or_404(Contact, pk=pk, resume__user=request.user)
    resume_pk = contact.resume.pk
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Контакт успешно удален!')
        return redirect('resume_detail', pk=resume_pk)
    
    context = {
        'contact': contact,
        'resume': contact.resume
    }
    
    return render(request, 'resumes/contact_confirm_delete.html', context)


# CRUD операции для языков
@login_required
def language_create(request, resume_pk):
    """Создание языка для резюме"""
    resume = get_object_or_404(Resume, pk=resume_pk, user=request.user)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        if form.is_valid():
            language = form.save(commit=False)
            language.resume = resume
            language.save()
            messages.success(request, 'Язык успешно добавлен!')
            return redirect('resume_detail', pk=resume.pk)
    else:
        form = LanguageForm()
    
    context = {
        'form': form,
        'resume': resume,
        'title': 'Добавить язык'
    }
    
    return render(request, 'resumes/language_form.html', context)


@login_required
def language_update(request, pk):
    """Редактирование языка"""
    language = get_object_or_404(Language, pk=pk, resume__user=request.user)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=language)
        if form.is_valid():
            form.save()
            messages.success(request, 'Язык успешно обновлен!')
            return redirect('resume_detail', pk=language.resume.pk)
    else:
        form = LanguageForm(instance=language)
    
    context = {
        'form': form,
        'language': language,
        'resume': language.resume,
        'title': 'Редактировать язык'
    }
    
    return render(request, 'resumes/language_form.html', context)


@login_required
def language_delete(request, pk):
    """Удаление языка"""
    language = get_object_or_404(Language, pk=pk, resume__user=request.user)
    resume_pk = language.resume.pk
    
    if request.method == 'POST':
        language.delete()
        messages.success(request, 'Язык успешно удален!')
        return redirect('resume_detail', pk=resume_pk)
    
    context = {
        'language': language,
        'resume': language.resume
    }
    
    return render(request, 'resumes/language_confirm_delete.html', context)