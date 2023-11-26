from django.contrib import admin
from .models import User, UserConfirmation


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone')

admin.site.register(User, UserAdmin)
admin.site.register(UserConfirmation)