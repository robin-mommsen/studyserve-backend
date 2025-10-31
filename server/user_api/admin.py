from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'coins']
    search_fields = ['email', 'username']
    ordering = ['email']
    exclude = ('is_superuser', 'is_staff', 'user_permissions', 'groups')

admin.site.register(User, UserAdmin)
