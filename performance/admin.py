from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Goal,PerformanceReview

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'status', 'deadline', 'get_creator')

    def get_creator(self, obj):
        if obj.created_by:
            return obj.created_by
        elif obj.created_by_user:
            return obj.created_by_user.username
        return "-"
    
    get_creator.short_description = "Assigned By"

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reviewer', 'rating', 'review_date')
    list_filter = ('rating',)
    search_fields = ('employee__name',)