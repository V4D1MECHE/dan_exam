from django.contrib import admin
from .models import veexam


class veexamAdmin(admin.ModelAdmin):
    # Поиск по названию экзамена и email пользователя
    search_fields = ['title', 'users__email']
    
    # Фильтры справа
    list_filter = ['is_public', 'created_at', 'exam_date']
    
    # Поля, отображаемые в списке
    list_display = ['title', 'exam_date', 'is_public', 'created_at']
    
    # Фильтр по конкретной дате экзамена (под строкой поиска)
    date_hierarchy = 'exam_date'
    
    # Настройка полей формы редактирования
    fields = ['title', 'exam_date', 'image', 'users', 'is_public']
    
    # Удобный виджет для M2M поля (горизонтальный фильтр)
    filter_horizontal = ['users']
    
    # Сортировка по умолчанию
    ordering = ['-exam_date']


admin.site.register(veexam, veexamAdmin)
