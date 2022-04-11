from django.contrib import admin
from .models import User


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'avatar',
        'phone', 'email_ver', 'last_login', 'date_joined', 'is_active',
        'is_staff', 'is_superuser', 'slug'
    )
    list_display_links = ('id', 'email')
    ordering = ('id',)
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {
            "fields": (
                (
                    'username', 'email', 'first_name', 'last_name', 'avatar',
                    'phone', 'email_ver', 'is_active', 'is_staff', 'slug'
                )
            ),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    prepopulated_fields = {'slug': ('username',)}


admin.site.register(User, AccountAdmin)
