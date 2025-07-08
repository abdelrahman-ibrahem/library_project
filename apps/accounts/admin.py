from django.contrib import admin
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdminView(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude',)
