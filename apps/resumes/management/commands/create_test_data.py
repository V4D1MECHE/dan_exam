from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from faker import Faker
from apps.resumes.models import (
    ResumeTemplate, Resume, Contact, WorkExperience,
    Education, Skill, Language, Award, Certificate,
    Recommendation, SharedLink
)

User = get_user_model()
fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Создает тестовые данные для приложения резюме'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создание шаблонов резюме
        templates = self.create_templates()
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(templates)} шаблонов резюме'))
        
        # Создание пользователей
        users = self.create_users(50)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(users)} пользователей'))
        
        # Создание резюме
        resumes = self.create_resumes(users, templates, 200)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(resumes)} резюме'))
        
        # Создание связанных данных для каждого резюме
        for resume in resumes:
            self.create_contacts(resume)
            self.create_work_experience(resume)
            self.create_education(resume)
            self.create_skills(resume)
            self.create_languages(resume)
            self.create_awards(resume)
            self.create_certificates(resume)
            self.create_recommendations(resume)
            self.create_shared_links(resume)
        
        self.stdout.write(self.style.SUCCESS('✓ Созданы все связанные данные'))
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
    
    def create_templates(self):
        templates_data = [
            {
                'name': 'Классический',
                'description': 'Традиционный шаблон резюме с четкой структурой',
                'is_default': True,
                'css_styles': {'font': 'Arial', 'color': '#000000'}
            },
            {
                'name': 'Современный',
                'description': 'Современный дизайн с акцентами и графическими элементами',
                'css_styles': {'font': 'Roboto', 'color': '#2c3e50'}
            },
            {
                'name': 'Минималистичный',
                'description': 'Простой и элегантный дизайн без лишних деталей',
                'css_styles': {'font': 'Helvetica', 'color': '#333333'}
            },
            {
                'name': 'Креативный',
                'description': 'Яркий и запоминающийся шаблон для творческих профессий',
                'css_styles': {'font': 'Montserrat', 'color': '#e74c3c'}
            },
            {
                'name': 'Профессиональный',
                'description': 'Строгий деловой стиль для руководителей',
                'css_styles': {'font': 'Times New Roman', 'color': '#1a1a1a'}
            }
        ]
        
        templates = []
        for data in templates_data:
            template, _ = ResumeTemplate.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            templates.append(template)
        
        return templates
    
    def create_users(self, count):
        users = []
        
        # Создание суперпользователя
        superuser, created = User.objects.get_or_create(
            email='admin@karrton.ru',
            defaults={
                'first_name': 'Vadim',
                'last_name': 'Erkhov',
                'middle_name': '',
                'is_staff': True,
                'is_superuser': True,
                'phone': '+7 (999) 123-45-67',
                'birth_date': datetime(1990, 1, 1).date()
            }
        )
        if created:
            superuser.set_password('admin')
            superuser.save()
        users.append(superuser)
        
        # Создание обычных пользователей
        for i in range(count - 1):
            user = User.objects.create(
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                middle_name=fake.middle_name() if random.choice([True, False]) else '',
                phone=fake.phone_number(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=65),
                is_active=True
            )
            user.set_password('password123')
            user.save()
            users.append(user)
        
        return users
    
    def create_resumes(self, users, templates, count):
        resumes = []
        positions = [
            'Python разработчик', 'Frontend разработчик', 'Data Scientist',
            'DevOps инженер', 'Менеджер проектов', 'UX/UI дизайнер',
            'Системный администратор', 'QA инженер', 'Android разработчик',
            'iOS разработчик', 'Full Stack разработчик', 'Бизнес-аналитик',
            'Product Manager', 'Scrum Master', 'Техлид'
        ]
        
        cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург',
                  'Нижний Новгород', 'Казань', 'Самара', 'Ростов-на-Дону']
        
        for i in range(count):
            user = random.choice(users)
            resume = Resume.objects.create(
                user=user,
                template=random.choice(templates),
                title=random.choice(positions),
                city=random.choice(cities),
                employment_type=random.choice(['FULL', 'PART', 'REMOTE', 'HYBRID']),
                salary_from=random.randint(50, 200) * 1000,
                salary_to=random.randint(200, 500) * 1000,
                currency='RUB',
                summary=fake.text(max_nb_chars=500),
                is_public=random.choice([True, False]),
                is_active=True
            )
            resumes.append(resume)
        
        return resumes
    
    def create_contacts(self, resume):
        # Основные контакты
        Contact.objects.create(
            resume=resume,
            contact_type='EMAIL',
            value=resume.user.email,
            is_primary=True,
            order=1
        )
        
        Contact.objects.create(
            resume=resume,
            contact_type='PHONE',
            value=resume.user.phone,
            is_primary=True,
            order=2
        )
        
        # Дополнительные контакты
        if random.choice([True, False]):
            Contact.objects.create(
                resume=resume,
                contact_type='TELEGRAM',
                value=f'@{fake.user_name()}',
                order=3
            )
        
        if random.choice([True, False]):
            Contact.objects.create(
                resume=resume,
                contact_type='GITHUB',
                value=f'github.com/{fake.user_name()}',
                order=4
            )
    
    def create_work_experience(self, resume):
        companies = ['Яндекс', 'Mail.ru Group', 'Сбербанк', 'Тинькофф',
                    'Авито', 'Ozon', 'Wildberries', 'X5 Retail Group']
        
        for i in range(random.randint(1, 4)):
            start_date = fake.date_between(start_date='-10y', end_date='-1y')
            end_date = fake.date_between(start_date=start_date, end_date='today')
            is_current = i == 0 and random.choice([True, False])
            
            WorkExperience.objects.create(
                resume=resume,
                company_name=random.choice(companies),
                position=resume.title,
                start_date=start_date,
                end_date=None if is_current else end_date,
                is_current=is_current,
                description=fake.text(max_nb_chars=300),
                achievements=fake.text(max_nb_chars=200),
                order=i + 1
            )
    
    def create_education(self, resume):
        universities = [
            'МГУ им. М.В. Ломоносова', 'МГТУ им. Н.Э. Баумана',
            'НИУ ВШЭ', 'МФТИ', 'СПбГУ', 'ИТМО', 'НГУ', 'УрФУ'
        ]
        
        faculties = [
            'Факультет вычислительной математики и кибернетики',
            'Факультет информационных технологий',
            'Факультет компьютерных наук',
            'Физико-технический факультет'
        ]
        
        Education.objects.create(
            resume=resume,
            institution_name=random.choice(universities),
            faculty=random.choice(faculties),
            degree=random.choice(['BACHELOR', 'MASTER']),
            field_of_study='Информатика и вычислительная техника',
            start_date=fake.date_between(start_date='-15y', end_date='-5y'),
            end_date=fake.date_between(start_date='-5y', end_date='-1y'),
            is_current=False,
            order=1
        )
    
    def create_skills(self, resume):
        tech_skills = [
            'Python', 'Django', 'JavaScript', 'React', 'Node.js',
            'PostgreSQL', 'MongoDB', 'Docker', 'Kubernetes', 'Git',
            'REST API', 'GraphQL', 'Redis', 'Celery', 'AWS'
        ]
        
        soft_skills = [
            'Командная работа', 'Коммуникабельность', 'Ответственность',
            'Управление временем', 'Критическое мышление'
        ]
        
        # Технические навыки
        for i, skill in enumerate(random.sample(tech_skills, random.randint(5, 10))):
            Skill.objects.create(
                resume=resume,
                name=skill,
                category='TECHNICAL',
                level=random.randint(3, 5),
                is_key_skill=i < 3,
                order=i + 1
            )
        
        # Гибкие навыки
        for i, skill in enumerate(random.sample(soft_skills, random.randint(2, 4))):
            Skill.objects.create(
                resume=resume,
                name=skill,
                category='SOFT',
                level=random.randint(3, 5),
                order=20 + i
            )
    
    def create_languages(self, resume):
        # Русский язык
        Language.objects.create(
            resume=resume,
            name='Русский',
            level='C2',
            is_native=True,
            order=1
        )
        
        # Английский язык
        Language.objects.create(
            resume=resume,
            name='Английский',
            level=random.choice(['B1', 'B2', 'C1']),
            is_native=False,
            order=2
        )
    
    def create_awards(self, resume):
        if random.choice([True, False]):
            Award.objects.create(
                resume=resume,
                title='Лучший сотрудник года',
                issuer=fake.company(),
                date=fake.date_between(start_date='-3y', end_date='today'),
                description='За выдающиеся достижения в работе',
                order=1
            )
    
    def create_certificates(self, resume):
        certs = [
            ('Python Professional Certificate', 'Coursera'),
            ('AWS Certified Solutions Architect', 'Amazon'),
            ('Google Cloud Professional', 'Google'),
            ('Certified Kubernetes Administrator', 'CNCF')
        ]
        
        for i, (name, issuer) in enumerate(random.sample(certs, random.randint(1, 3))):
            Certificate.objects.create(
                resume=resume,
                name=name,
                issuer=issuer,
                issue_date=fake.date_between(start_date='-2y', end_date='today'),
                credential_id=fake.uuid4()[:12].upper(),
                order=i + 1
            )
    
    def create_recommendations(self, resume):
        if random.choice([True, False]):
            Recommendation.objects.create(
                resume=resume,
                recommender_name=fake.name(),
                recommender_position='Руководитель отдела разработки',
                recommender_company=fake.company(),
                recommender_phone=fake.phone_number(),
                recommender_email=fake.email(),
                relationship='Непосредственный руководитель',
                text=fake.text(max_nb_chars=300),
                order=1
            )
    
    def create_shared_links(self, resume):
        if resume.is_public and random.choice([True, False]):
            SharedLink.objects.create(
                resume=resume,
                link_type=random.choice(['PUBLIC', 'PROTECTED', 'TEMPORARY']),
                is_active=True,
                expires_at=timezone.now() + timedelta(days=30) if random.choice([True, False]) else None
            )