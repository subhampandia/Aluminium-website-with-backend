from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'status', 'deadline')
    list_filter = ('status',)