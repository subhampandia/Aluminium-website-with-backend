from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse

from .models import Department, Designation, Employee, Shift, ShiftAssignment, Leave, Attendance


# ================= AUTH =================
def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔀 Redirect based on role
            if hasattr(user, 'employee_profile'):
                return redirect('employee_dashboard')
            else:
                return redirect('dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

@login_required
def employee_profile(request):
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        return redirect('employee_add')  # safety fallback

    return render(request, 'employee/profile.html', {
        'employee': employee
    })

@never_cache
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')


# ================= DEPARTMENT =================

@login_required(login_url='login')
def department_list(request):
    return render(request, 'department/department_list.html', {
        'departments': Department.objects.all().order_by('id')
    })


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
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.name = request.POST.get('name')
        dept.description = request.POST.get('description')
        dept.save()
        messages.success(request, "Department updated")
        return redirect('department_list')
    return render(request, 'department/department_edit.html', {'department': dept})


@login_required(login_url='login')
def department_delete(request, pk):
    get_object_or_404(Department, pk=pk).delete()
    messages.success(request, "Department deleted")
    return redirect('department_list')


# ================= DESIGNATION =================

@login_required(login_url='login')
def designation_list(request):
    return render(request, 'designation/designation_list.html', {
        'designations': Designation.objects.select_related('department')
    })


@login_required(login_url='login')
def designation_add(request):
    if request.method == 'POST':
        Designation.objects.create(
            department_id=request.POST.get('department'),
            name=request.POST.get('name')
        )
        messages.success(request, "Designation added")
        return redirect('designation_list')
    return render(request, 'designation/designation_add.html', {
        'departments': Department.objects.all()
    })


@login_required(login_url='login')
def designation_edit(request, pk):
    des = get_object_or_404(Designation, pk=pk)
    if request.method == 'POST':
        des.department_id = request.POST.get('department')
        des.name = request.POST.get('name')
        des.save()
        messages.success(request, "Designation updated")
        return redirect('designation_list')
    return render(request, 'designation/designation_edit.html', {
        'designation': des,
        'departments': Department.objects.all()
    })


@login_required(login_url='login')
def designation_delete(request, pk):
    get_object_or_404(Designation, pk=pk).delete()
    messages.success(request, "Designation deleted")
    return redirect('designation_list')


# ================= EMPLOYEE =================

@login_required(login_url='login')
def employee_list(request):
    return render(request, 'employee/employee_list.html', {
        'employees': Employee.objects.select_related('department', 'designation')
    })


@login_required(login_url='login')
def employee_add(request):
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == 'POST':

        # CREATE USER
        username = request.POST.get('user_id')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User ID already exists")
            return redirect('employee_add')

        user = User.objects.create_user(username=username, password=password)

        current_address = f"{request.POST.get('current_line1')}\n{request.POST.get('current_line2')}\n{request.POST.get('current_city')}, {request.POST.get('current_state')} - {request.POST.get('current_pin')}"
        permanent_address = f"{request.POST.get('permanent_line1')}\n{request.POST.get('permanent_line2')}\n{request.POST.get('permanent_city')}, {request.POST.get('permanent_state')} - {request.POST.get('permanent_pin')}"

        Employee.objects.create(
            user=user,
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
            Aadhar_no=request.POST.get('Aadhar_no'),
            Bank_name=request.POST.get('Bank_name'),
            branch_name=request.POST.get('branch_name'),
            acc_no=request.POST.get('acc_no'),
            ifsc_no=request.POST.get('ifsc_code'),
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
    return render(request, 'employee/employee_view.html', {
        'employee': get_object_or_404(Employee, pk=pk)
    })


@login_required(login_url='login')
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == 'POST':

        # ================= EMPLOYEE FIELDS =================
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
        employee.Aadhar_no = request.POST.get('Aadhar_no')
        employee.Bank_name = request.POST.get('Bank_name')
        employee.branch_name = request.POST.get('branch_name')
        employee.acc_no = request.POST.get('acc_no')
        employee.ifsc_no = request.POST.get('ifsc_no')

        employee.father_name = request.POST.get('father_name')
        employee.mother_name = request.POST.get('mother_name')

        if request.FILES.get('photo'):
            employee.photo = request.FILES.get('photo')

        # ================= USER (LOGIN) FIELDS =================
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        if employee.user:
            user = employee.user

            # Update username
            if username:
                user.username = username

            # Update password ONLY if entered
            if new_password:
                user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # 🔥 THIS LINE


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
    emp = get_object_or_404(Employee, pk=pk)
    if emp.user:
        emp.user.delete()
    emp.delete()
    messages.success(request, "Employee deleted")
    return redirect('employee_list')


@login_required(login_url='login')
def employee_toggle_status(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    emp.is_active = not emp.is_active
    emp.save()
    if emp.user:
        emp.user.is_active = emp.is_active
        emp.user.save()
    messages.success(request, "Employee status updated")
    return redirect('employee_list')


# ================= SHIFT =================

@login_required(login_url='login')
def shift_list(request):
    return render(request, 'shift/shift_list.html', {
        'shifts': Shift.objects.all()
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
        messages.success(request, "Shift added")
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
        messages.success(request, "Shift updated")
        return redirect('shift_list')
    return render(request, 'shift/shift_edit.html', {'shift': shift})


@login_required(login_url='login')
def shift_toggle_status(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    shift.is_active = not shift.is_active
    shift.save()
    return redirect('shift_list')


# ================= SHIFT ASSIGN =================

@login_required(login_url='login')
def shift_assign(request):
    if request.method == 'POST':
        ShiftAssignment.objects.update_or_create(
            employee_id=request.POST.get('employee'),
            defaults={'shift_id': request.POST.get('shift'), 'is_active': True}
        )
        messages.success(request, "Shift assigned")
        return redirect('shift_assign_list')

    return render(request, 'shift/shift_assign.html', {
        'employees': Employee.objects.filter(is_active=True),
        'shifts': Shift.objects.filter(is_active=True)
    })


@login_required(login_url='login')
def shift_assign_list(request):
    return render(request, 'shift/shift_assign_list.html', {
        'assignments': ShiftAssignment.objects.select_related(
            'employee__department', 'employee__designation', 'shift'
        )
    })


@login_required(login_url='login')
def shift_assign_edit(request, pk):
    assignment = get_object_or_404(ShiftAssignment, pk=pk)
    if request.method == 'POST':
        assignment.shift_id = request.POST.get('shift')
        assignment.save()
        messages.success(request, "Shift reassigned")
        return redirect('shift_assign_list')
    return render(request, 'shift/shift_assign_edit.html', {
        'assignment': assignment,
        'shifts': Shift.objects.filter(is_active=True)
    })


# ================= AJAX =================

@login_required(login_url='login')
def get_all_employees(request):
    data = [{
        'id': e.id,
        'emp_id': e.employee_id,
        'name': e.full_name(),
        'department': e.department.name,
        'designation': e.designation.name
    } for e in Employee.objects.select_related('department', 'designation')]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
def employee_dashboard(request):
    employee = get_object_or_404(Employee, user=request.user)
    return render(request, 'employee/employee_dashboard.html', {
        'employee': employee
    })
@login_required(login_url='login')
def apply_leave(request):
    employee = get_object_or_404(Employee, user=request.user)

    if request.method == 'POST':
        Leave.objects.create(
            employee=employee,
            leave_type=request.POST.get('leave_type'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            reason=request.POST.get('reason')
        )
        messages.success(request, "Leave applied successfully")
        return redirect('my_leaves')

    return render(request, 'employee/apply_leave.html')
@login_required(login_url='login')
def my_leaves(request):
    employee = get_object_or_404(Employee, user=request.user)
    leaves = employee.leaves.all().order_by('-applied_at')

    return render(request, 'employee/my_leaves.html', {
        'leaves': leaves
    })

@login_required(login_url='login')
def admin_leave_list(request):
    leaves = Leave.objects.select_related(
        'employee__department',
        'employee__designation'
    ).order_by('-applied_at')

    return render(request, 'leave/admin_leave_list.html', {
        'leaves': leaves
    })

@login_required(login_url='login')
def admin_leave_action(request, pk, action):
    leave = get_object_or_404(Leave, pk=pk)

    if request.method == 'POST':
        if action == 'approve':
            leave.status = 'Approved'
            leave.rejection_reason = None

        elif action == 'reject':
            leave.status = 'Rejected'
            leave.rejection_reason = request.POST.get('rejection_reason')

        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()

        messages.success(request, f"Leave {leave.status.lower()} successfully")

    return redirect('admin_leave_list')

@login_required
def employee_attendance_history(request):
    employee = request.user.employee_profile
    attendances = Attendance.objects.filter(employee=employee)

    return render(
        request,
        'attendance/employee_attendance_history.html',
        {'attendances': attendances}    
    )
@login_required
def punch_in(request):
    employee = request.user.employee_profile
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )

    if attendance.punch_in:
        messages.warning(request, "You have already punched in today.")
    else:
        attendance.punch_in = now_time
        attendance.save()
        messages.success(request, "Punch in successful.")

    return redirect('employee_attendance_history')