from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Designation, Employee, Shift


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


@never_cache
def logout_view(request):
    logout(request)
    return redirect('index')


@never_cache
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')


# ================= DEPARTMENT =================

@never_cache
@login_required(login_url='login')
def department_list(request):
    departments = Department.objects.all().order_by('id')
    return render(request, 'department/department_list.html', {
        'departments': departments
    })


@login_required(login_url='login')
def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            Department.objects.create(
                name=name,
                description=description
            )
            messages.success(request, "Department added successfully")
            return redirect('department_list')

    return render(request, 'department/department_add.html')


@login_required(login_url='login')
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        department.name = request.POST.get('name')
        department.description = request.POST.get('description')
        department.save()
        messages.success(request, "Department updated successfully")
        return redirect('department_list')

    return render(request, 'department/department_edit.html', {
        'department': department
    })


@login_required(login_url='login')
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.delete()
    messages.success(request, "Department deleted successfully")
    return redirect('department_list')

@never_cache
@login_required(login_url='login')
def designation_list(request):
    designations = Designation.objects.select_related('department').all()
    return render(request, 'designation/designation_list.html', {
        'designations': designations
    })


@login_required(login_url='login')
def designation_add(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        department_id = request.POST.get('department')
        name = request.POST.get('name')

        if department_id and name:
            Designation.objects.create(
                department_id=department_id,
                name=name
            )
            messages.success(request, "Designation added successfully")
            return redirect('designation_list')

    return render(request, 'designation/designation_add.html', {
        'departments': departments
    })


@login_required(login_url='login')
def designation_edit(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    departments = Department.objects.all()

    if request.method == 'POST':
        designation.department_id = request.POST.get('department')
        designation.name = request.POST.get('name')
        designation.save()
        messages.success(request, "Designation updated successfully")
        return redirect('designation_list')

    return render(request, 'designation/designation_edit.html', {
        'designation': designation,
        'departments': departments
    })


@login_required(login_url='login')
def designation_delete(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    designation.delete()
    messages.success(request, "Designation deleted successfully")
    return redirect('designation_list')

@never_cache
@login_required(login_url='login')
def employee_list(request):
    employees = Employee.objects.select_related(
        'department', 'designation'
    ).all()

    return render(request, 'employee/employee_list.html', {
        'employees': employees
    })

@login_required(login_url='login')
def employee_add(request):
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == 'POST':
        Employee.objects.create(
            first_name=request.POST.get('first_name'),
            middle_name=request.POST.get('middle_name'),
            last_name=request.POST.get('last_name'),
            gender=request.POST.get('gender'),
            blood_group=request.POST.get('blood_group'),
            photo=request.FILES.get('photo'),   # ✅ THIS LINE

            email=request.POST.get('email'),
            contact_no=request.POST.get('contact_no'),
            emergency_contact=request.POST.get('emergency_contact'),
            address=request.POST.get('address'),
            permanent_address=request.POST.get('permanent_address'),

            employee_id=request.POST.get('employee_id'),
            department_id=request.POST.get('department'),
            designation_id=request.POST.get('designation'),

            father_name=request.POST.get('father_name'),
            mother_name=request.POST.get('mother_name'),

            created_by=request.user
        )

        messages.success(request, "Employee added successfully")
        return redirect('employee_list')

    return render(request, 'employee/employee_add.html', {
        'departments': departments,
        'designations': designations
    })
@login_required(login_url='login')
def employee_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee/employee_view.html', {
        'employee': employee
    })

@login_required(login_url='login')
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name')
        employee.middle_name = request.POST.get('middle_name')
        employee.last_name = request.POST.get('last_name')
        employee.gender = request.POST.get('gender')
        employee.blood_group = request.POST.get('blood_group')

        employee.email = request.POST.get('email')
        employee.contact_no = request.POST.get('contact_no')
        employee.emergency_contact = request.POST.get('emergency_contact')
        employee.address = request.POST.get('address')
        employee.permanent_address = request.POST.get('permanent_address')

        employee.employee_id = request.POST.get('employee_id')
        employee.department_id = request.POST.get('department')
        employee.designation_id = request.POST.get('designation')

        employee.father_name = request.POST.get('father_name')
        employee.mother_name = request.POST.get('mother_name')

        # PHOTO (only update if new one is uploaded)
        if request.FILES.get('photo'):
            employee.photo = request.FILES.get('photo')

        employee.save()
        messages.success(request, "Employee updated successfully")
        return redirect('employee_list')

    return render(request, 'employee/employee_edit.html', {
        'employee': employee,
        'departments': departments,
        'designations': designations
    })

@login_required(login_url='login')
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    messages.success(request, "Employee deleted successfully")
    return redirect('employee_list')

@login_required(login_url='login')
def employee_toggle_status(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = not employee.is_active
    employee.save()

    status = "activated" if employee.is_active else "deactivated"
    messages.success(request, f"Employee {status} successfully")

    return redirect('employee_list')

@never_cache
@login_required(login_url='login')
def shift_list(request):
    shifts = Shift.objects.all().order_by('id')
    return render(request, 'shift/shift_list.html', {
        'shifts': shifts
    })


@login_required(login_url='login')
def shift_add(request):
    if request.method == 'POST':
        Shift.objects.create(
            name=request.POST.get('name'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            break_minutes=request.POST.get('break_minutes') or 0
        )
        messages.success(request, "Shift added successfully")
        return redirect('shift_list')

    return render(request, 'shift/shift_add.html')


@login_required(login_url='login')
def shift_edit(request, pk):
    shift = get_object_or_404(Shift, pk=pk)

    if request.method == 'POST':
        shift.name = request.POST.get('name')
        shift.start_time = request.POST.get('start_time')
        shift.end_time = request.POST.get('end_time')
        shift.break_minutes = request.POST.get('break_minutes') or 0
        shift.save()

        messages.success(request, "Shift updated successfully")
        return redirect('shift_list')

    return render(request, 'shift/shift_edit.html', {
        'shift': shift
    })


@login_required(login_url='login')
def shift_toggle_status(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    shift.is_active = not shift.is_active
    shift.save()

    return redirect('shift_list')
