from django.contrib import admin
from .models import (
    Department,
    Designation,
    Employee,
    Shift,
    ShiftAssignment,
    Attendance,
    Holiday,
    Leave
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
        'is_processed'
    )
    list_filter = ('status', 'date')
    search_fields = ('employee__employee_id','employee_first_name')
    date_hierarchy = 'date'

# ------------------------
# Holiday
# ------------------------

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_filter = ('date',)
    
    
# ------------------------
# Leave
# ------------------------    
    
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'leave_type',
        'start_date',
        'end_date',
        'status'
    )
    list_filter = ('leave_type', 'status')
    search_fields = ('employee__employee_id', 'employee__first_name')

from .models import MonthlySalary

@admin.register(MonthlySalary)
class MonthlySalaryAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "month",
        "year",
        "gross_salary",
        "leave_deduction",
        "emp_pf",
        "emp_esic",
        "net_salary",
        "generated_at"
    )

    list_filter = ("month", "year")
    search_fields = ("employee__employee_id", "employee__first_name")
    
