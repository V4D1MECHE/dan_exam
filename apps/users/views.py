from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


def register(request):
    """Регистрация пользователя с кастомной формой"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт успешно создан для {user.email}!')
            # Автоматически входим после регистрации
            login(request, user)
            return redirect('my_resumes')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """Профиль пользователя"""
    return render(request, 'users/profile.html', {'user': request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        """Возвращаем текущего пользователя"""
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)