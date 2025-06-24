# Generated manually to create SkillTag and SkillTagRelation models

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0006_remove_unused_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название тега')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('color', models.CharField(default='#007bff', max_length=7, verbose_name='Цвет')),
                ('is_popular', models.BooleanField(default=False, verbose_name='Популярный')),
                ('created_at', models.DateTimeField(default=timezone.now, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Тег навыка',
                'verbose_name_plural': 'Теги навыков',
                'ordering': ['-is_popular', 'name'],
            },
        ),
        migrations.CreateModel(
            name='SkillTagRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proficiency_level', models.IntegerField(choices=[(1, 'Начальный'), (2, 'Базовый'), (3, 'Средний'), (4, 'Продвинутый'), (5, 'Эксперт')], default=3, verbose_name='Уровень владения')),
                ('years_of_experience', models.PositiveIntegerField(default=0, verbose_name='Лет опыта')),
                ('last_used', models.DateField(blank=True, null=True, verbose_name='Последнее использование')),
                ('is_certified', models.BooleanField(default=False, verbose_name='Есть сертификат')),
                ('created_at', models.DateTimeField(default=timezone.now, verbose_name='Дата создания')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resumes.skill', verbose_name='Навык')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resumes.skilltag', verbose_name='Тег')),
            ],
            options={
                'verbose_name': 'Связь навык-тег',
                'verbose_name_plural': 'Связи навыков и тегов',
                'ordering': ['-proficiency_level', '-years_of_experience'],
            },
        ),
        migrations.AddField(
            model_name='skill',
            name='tags',
            field=models.ManyToManyField(blank=True, through='resumes.SkillTagRelation', to='resumes.skilltag', verbose_name='Теги'),
        ),
        migrations.AlterUniqueTogether(
            name='skilltagrelation',
            unique_together={('skill', 'tag')},
        ),
    ]