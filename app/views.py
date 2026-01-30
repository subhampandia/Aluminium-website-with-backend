from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import (
    Department,
    Designation,
    Employee,
    Shift,
    ShiftAssignment
)

# ================= AUTH =================

def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
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

@login_required(login_url='login')
def department_list(request):
    departments = Department.objects.all().order_by('id')
    return render(request, 'department/department_list.html', {'departments': departments})


@login_required(login_url='login')
def department_add(request):
    if request.method == 'POST':
        Department.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description')
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

    return render(request, 'department/department_edit.html', {'department': department})


@login_required(login_url='login')
def department_delete(request, pk):
    get_object_or_404(Department, pk=pk).delete()
    messages.success(request, "Department deleted successfully")
    return redirect('department_list')


# ================= DESIGNATION =================

@login_required(login_url='login')
def designation_list(request):
    designations = Designation.objects.select_related('department')
    return render(request, 'designation/designation_list.html', {'designations': designations})


@login_required(login_url='login')
def designation_add(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        Designation.objects.create(
            department_id=request.POST.get('department'),
            name=request.POST.get('name')
        )
        messages.success(request, "Designation added successfully")
        return redirect('designation_list')

    return render(request, 'designation/designation_add.html', {'departments': departments})


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
    get_object_or_404(Designation, pk=pk).delete()
    messages.success(request, "Designation deleted successfully")
    return redirect('designation_list')


# ================= EMPLOYEE =================

@login_required(login_url='login')
def employee_list(request):
    employees = Employee.objects.select_related('department', 'designation')
    return render(request, 'employee/employee_list.html', {'employees': employees})


@login_required(login_url='login')
def employee_add(request):
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == 'POST':

        current_address = (
            f"{request.POST.get('current_line1')}\n"
            f"{request.POST.get('current_line2')}\n"
            f"{request.POST.get('current_city')}, "
            f"{request.POST.get('current_state')} - "
            f"{request.POST.get('current_pin')}"
        )

        permanent_address = (
            f"{request.POST.get('permanent_line1')}\n"
            f"{request.POST.get('permanent_line2')}\n"
            f"{request.POST.get('permanent_city')}, "
            f"{request.POST.get('permanent_state')} - "
            f"{request.POST.get('permanent_pin')}"
        )

        Employee.objects.create(
            first_name=request.POST.get('first_name'),
            middle_name=request.POST.get('middle_name'),
            last_name=request.POST.get('last_name'),
            gender=request.POST.get('gender'),
            blood_group=request.POST.get('blood_group'),
            date_of_birth=request.POST.get('date_of_birth') or None,
            date_of_joining=request.POST.get('date_of_joining') or None,
            generated_at=request.POST.get('generated_at') or None,

            email=request.POST.get('email'),
            contact_no=request.POST.get('contact_no'),
            emergency_contact=request.POST.get('emergency_contact'),

            employee_id=request.POST.get('employee_id'),
            department_id=request.POST.get('department'),
            designation_id=request.POST.get('designation'),

            bachelor_degree=request.POST.get('bachelor_degree'),
            master_degree=request.POST.get('master_degree'),

            pan_no=request.POST.get('pan_no'),
            Aadhaar_no=request.POST.get('Aadhaar_no'),

            Bank_name=request.POST.get('Bank_name'),
            branch_name=request.POST.get('branch_name'),
            acc_no=request.POST.get('acc_no'),
            ifsc_code=request.POST.get('ifsc_code'),

            father_name=request.POST.get('father_name'),
            mother_name=request.POST.get('mother_name'),

            address=current_address,
            permanent_address=permanent_address,

            photo=request.FILES.get('photo'),
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
    return render(request, 'employee/employee_view.html', {'employee': employee})


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
        employee.date_of_birth = request.POST.get('date_of_birth') or None
        employee.date_of_joining = request.POST.get('date_of_joining') or None
        employee.generated_at = request.POST.get('generated_at') or None

        employee.employee_id = request.POST.get('employee_id')
        employee.department_id = request.POST.get('department')
        employee.designation_id = request.POST.get('designation')

        employee.pan_no = request.POST.get('pan_no')
        employee.Aadhaar_no = request.POST.get('Aadhaar_no')
        employee.Bank_name = request.POST.get('Bank_name')
        employee.branch_name = request.POST.get('branch_name')
        employee.acc_no = request.POST.get('acc_no')
        employee.ifsc_code = request.POST.get('ifsc_code')

        employee.father_name = request.POST.get('father_name')
        employee.mother_name = request.POST.get('mother_name')

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
    get_object_or_404(Employee, pk=pk).delete()
    messages.success(request, "Employee deleted successfully")
    return redirect('employee_list')


@login_required(login_url='login')
def employee_toggle_status(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = not employee.is_active
    employee.save()
    messages.success(request, "Employee status updated")
    return redirect('employee_list')


# ================= SHIFT =================

@login_required(login_url='login')
def shift_list(request):
    shifts = Shift.objects.all().order_by('id')
    return render(request, 'shift/shift_list.html', {'shifts': shifts})


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

    return render(request, 'shift/shift_edit.html', {'shift': shift})


@login_required(login_url='login')
def shift_toggle_status(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    shift.is_active = not shift.is_active
    shift.save()
    return redirect('shift_list')


# ================= SHIFT ASSIGNMENT =================

@login_required(login_url='login')
def shift_assign(request):
    shifts = Shift.objects.filter(is_active=True)

    if request.method == "POST":
        employee_ids = request.POST.getlist('employees')
        shift_id = request.POST.get('shift')

        for emp_id in employee_ids:
            ShiftAssignment.objects.update_or_create(
                employee_id=emp_id,
                defaults={'shift_id': shift_id, 'is_active': True}
            )

        messages.success(request, "Shift assigned successfully")
        return redirect('shift_assign_list')

    return render(request, 'shift/shift_assign.html', {'shifts': shifts})


@login_required(login_url='login')
def shift_assign_list(request):
    assignments = ShiftAssignment.objects.select_related(
        'employee__department',
        'employee__designation',
        'shift'
    ).filter(is_active=True)

    return render(request, 'shift/shift_assign_list.html', {
        'assignments': assignments
    })


# ================= AJAX =================

@login_required(login_url='login')
def get_all_employees(request):
    employees = Employee.objects.select_related('department', 'designation')

    data = []
    for e in employees:
        data.append({
            'id': e.id,
            'emp_id': e.employee_id,
            'name': f"{e.first_name} {e.last_name}",
            'department': e.department.name if e.department else '',
            'designation': e.designation.name if e.designation else '',
        })

    return JsonResponse(data, safe=False)
@login_required(login_url='login')
def shift_assign_edit(request, pk):
    assignment = get_object_or_404(ShiftAssignment, pk=pk)
    shifts = Shift.objects.filter(is_active=True)

    if request.method == 'POST':
        assignment.shift_id = request.POST.get('shift')
        assignment.save()

        messages.success(request, "Shift reassigned successfully")
        return redirect('shift_assign_list')

    return render(request, 'shift/shift_assign_edit.html', {
        'assignment': assignment,
        'shifts': shifts
    })
