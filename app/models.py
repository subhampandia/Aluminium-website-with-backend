from django.db import models

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Designation(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
