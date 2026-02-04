from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Designation(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Employee(models.Model):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    BACHELOR_CHOICES = [
        ('BCom', 'B.Com'),
        ('BSc', 'B.Sc'),
        ('BA', 'B.A'),
        ('BTech', 'B.Tech'),
    ]

    MASTER_CHOICES = [
        ('MCom', 'M.Com'),
        ('MSc', 'M.Sc'),
        ('MA', 'M.A'),
        ('MTech', 'M.Tech'),
    ]

    # Personal
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10,choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_profile') 

    
    # Contact
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    #education
    bachelor_degree = models.CharField(max_length=10, choices=BACHELOR_CHOICES, blank=True, null=True)
    master_degree = models.CharField(max_length=10, choices=MASTER_CHOICES, blank=True, null=True)
    # Work
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT)
    date_of_joining = models.DateField(blank=True, null=True)


    # Media
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)

    #Bank details

    pan_no = models.CharField(max_length=10,blank=True,null=True)
    Aadhar_no = models.CharField(max_length=12,blank=True,null=True)
    Bank_name = models.CharField(max_length=50,blank=True,null=True)
    acc_no = models.CharField(max_length=15,blank=True,null=True)
    ifsc_no = models.CharField(max_length=15,blank=True,null=True)
    branch_name = models.CharField(max_length=50,blank=True,null=True)

    # System
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    generated_at = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_employees')

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
    
class ShiftAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.employee.first_name} - {self.shift.name}"

class Leave(models.Model):

    LEAVE_TYPE_CHOICES = [
        ('CL', 'Casual Leave'),
        ('SL', 'Sick Leave'),
        ('PL', 'Paid Leave'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='leaves')
    leave_type = models.CharField(max_length=20,choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)

    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type} ({self.status})"

class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records")
    date = models.DateField(default=timezone.now)
    punch_in = models.TimeField(null=True, blank=True)
    punch_out = models.TimeField(null=True, blank=True)
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True)
    status = models.CharField(
    max_length=20,
    choices=[
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
    ],
    default='Present')
    class Meta:
        ordering = ['-date']
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.date}"
    

