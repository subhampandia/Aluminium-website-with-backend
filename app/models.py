from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Designation(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Employee(models.Model):

    # Personal
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(
        max_length=10,
        choices=[('Male','Male'),('Female','Female'),('Other','Other')]
    )
    blood_group = models.CharField(max_length=10, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    # Contact
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)


    # Work
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)

    # Media
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)

    # System
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name()} ({self.employee_id})"
   
class Shift(models.Model):

    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
