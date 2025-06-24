from django.shortcuts import redirect, render
from django.http import Http404
from django.urls import resolve, Resolver404


class RedirectToHomeMiddleware:
    """Middleware для обработки ошибок 404"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Проверяем статус ответа
        if response.status_code == 404:
            # Показываем красивую страницу 404 с автоматическим редиректом
            return render(request, '404.html', status=404)
        
        return response

    def process_exception(self, request, exception):
        """Обрабатываем исключения"""
        if isinstance(exception, (Http404, Resolver404)):
            # Показываем красивую страницу 404 с автоматическим редиректом
            return render(request, '404.html', status=404)
        return None