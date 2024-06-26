from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('password',)
    list_filter = ['username', 'email']
    list_display = ['username', 'email', 'first_name']


admin.site.register(User, UserAdmin)
