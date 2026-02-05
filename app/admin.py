from django.contrib import admin
from .models import (
    Department,
    Designation,
    Employee,
    Shift,
    ShiftAssignment,
    Attendance,
)

# ------------------------
# Department
# ------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


# ------------------------
# Designation
# ------------------------
@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name',)


# ------------------------
# Employee
# ------------------------
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'full_name',
        'department',
        'designation',
        'is_active',
    )
    list_filter = ('department', 'designation', 'is_active')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')
    ordering = ('employee_id',)


# ------------------------
# Shift
# ------------------------
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_time',
        'end_time',
        'break_minutes',
        'is_active',
    )
    list_filter = ('is_active',)
    search_fields = ('name',)


# ------------------------
# Shift Assignment
# ------------------------
@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'shift',
        'assigned_date',
        'is_active',
    )
    list_filter = ('shift', 'is_active')
    search_fields = ('employee__employee_id',)


# ------------------------
# Attendance
# ------------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'date',
        'punch_in',
        'punch_out',
        'working_hours',
        'status',
    )
    list_filter = ('status', 'date')
    search_fields = ('employee__employee_id',)
    date_hierarchy = 'date'
