from django.shortcuts import render
from .models import veexam


def veexam_list(request):
    # Получаем только опубликованные записи
    exams = veexam.objects.filter(is_public=True).order_by('-exam_date')
    
    context = {
        'exams': exams,
        'full_name': 'Vadim Erkhov',
        'group': '231-365'  # Замените на номер вашей группы
    }
    
    return render(request, 'exams/veexam_list.html', context)
