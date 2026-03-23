# Create your models here.
from django.db import models
from app.models import Employee
from django.contrib.auth.models import User# adjust if needed

class Goal(models.Model):
    STATUS_CHOICES = [
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Employee, related_name='goals_created', on_delete=models.SET_NULL, null=True,blank=True)
    created_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ✅ NEW

    title = models.CharField(max_length=200)
    description = models.TextField()
    achieved_value = models.IntegerField(default=0,blank=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Assigned')
    submitted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.title}"
    
class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Employee, related_name='reviewer', on_delete=models.SET_NULL, null=True)

    RATING_CHOICES = [
        (5, 'Outstanding'),
        (4, 'Exceeds Expectations'),
        (3, 'Meets Expectations'),
        (2, 'Needs Improvement'),
        (1, 'Poor'),
    ]

    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField()
    review_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.rating}"