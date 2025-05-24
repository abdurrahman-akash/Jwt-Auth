from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'role', 'status', 'is_staff', 'is_active')
    list_filter = ('role', 'status', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Fields to display in the admin detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Roles and Status', {'fields': ('role', 'status')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'role', 'status', 'is_staff', 'is_active'),
        }),
    )

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser)