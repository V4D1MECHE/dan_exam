from django.db import models
from django.contrib.auth.models import User


class veexam(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название экзамена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')
    exam_date = models.DateTimeField(verbose_name='Дата проведения экзамена')
    image = models.ImageField(upload_to='exams/', blank=True, null=True, verbose_name='Изображение')
    users = models.ManyToManyField(User, related_name='veexams', verbose_name='Пользователи')
    is_public = models.BooleanField(default=False, verbose_name='Опубликовано')
    
    class Meta:
        verbose_name = 'VE Экзамен'
        verbose_name_plural = 'VE Экзамены'
        ordering = ['-exam_date']
    
    def __str__(self):
        return self.title
