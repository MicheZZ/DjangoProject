from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'balance', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Профиль', {
            'fields': ('avatar', 'bio', 'balance')
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )
