"""
URL configuration for karrton project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps.resumes import views as resume_views
from django.shortcuts import redirect

# Обработчики ошибок
def redirect_to_home(request, exception=None):
    """Редирект на главную страницу при любых ошибках"""
    return redirect('/')

# Устанавливаем обработчики ошибок
handler404 = redirect_to_home
handler500 = redirect_to_home
handler403 = redirect_to_home
handler400 = redirect_to_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.resumes.api_urls')),
    path('', include('apps.resumes.urls')),
    path('users/', include('apps.users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    
    # Регулярные выражения в URLs
    re_path(r'^resume/(?P<pk>\d+)/$', resume_views.resume_detail, name='resume_detail_regex'),
    re_path(r'^resumes/(?P<year>\d{4})/$', resume_views.resumes_by_year, name='resumes_by_year'),
    
    # Catch-all pattern - должен быть последним
    re_path(r'^.*/$', redirect_to_home, name='catch_all'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
