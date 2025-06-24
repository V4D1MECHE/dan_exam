from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'phone', 'is_active', 'date_joined', 'get_resumes_count']
    list_filter = ['is_active', 'date_joined', 'birth_date']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    list_display_links = ['email', 'get_full_name']
    readonly_fields = ['date_joined', 'last_login']
    date_hierarchy = 'date_joined'
    
    @admin.display(description='ФИО')
    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name or ''}".strip()
    
    @admin.display(description='Количество резюме')
    def get_resumes_count(self, obj):
        return obj.resumes.count()
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'phone', 'birth_date')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    ordering = ('email',)
    filter_horizontal = ['groups', 'user_permissions']