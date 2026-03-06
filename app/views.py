from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import localdate
from datetime import date
import calendar
import json
from decimal import Decimal

from .utils import get_working_days_of_month, get_used_pl,generate_salary
from .models import Department, Designation, Employee, Shift, ShiftAssignment, Leave, Attendance, Holiday,AttendanceRegularization


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


def generate_employee_id():
    year = timezone.now().year % 100  # 2026 → 26
    prefix = f"EMP{year}"

    last_employee = Employee.objects.filter(
        employee_id__startswith=prefix
    ).order_by('-employee_id').first()

    if last_employee:
        last_number = int(last_employee.employee_id[-4:])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"

@login_required(login_url='login')
def employee_add(request):
    departments = Department.objects.all()
    designations = Designation.objects.all()

    generated_emp_id = generate_employee_id()

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
            employee_id=generated_emp_id,
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
        'designations': designations,
        'generated_emp_id': generated_emp_id,  # ✅ REQUIRED

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
@login_required
def employee_shift_details(request):
    employee = request.user.employee_profile

    active_shift = ShiftAssignment.objects.filter(
        employee=employee,
        is_active=True
    ).select_related('shift').first()

    shift_history = ShiftAssignment.objects.filter(
        employee=employee,
        is_active=False
    ).select_related('shift')

    return render(
        request,
        'employee/employee_shift_details.html',
        {
            'active_shift': active_shift,
            'shift_history': shift_history
        }
    )


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
    today = timezone.localdate()

    today_attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    return render(request, 'employee/employee_dashboard.html', {
        'employee': employee,
        'today_attendance': today_attendance,   # ✅ THIS WAS MISSING
    })


# ================= LEAVE  =================

    
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

        if action == 'approve' and leave.status != 'Approved':
            leave.status = 'Approved'
            leave.rejection_reason = None

            # 🔥 Calculate total leave days
            total_days = (leave.end_date - leave.start_date).days + 1

            # 🔥 Deduct from LWP balance (can go negative)
            employee = leave.employee
            employee.lwp_balance -= total_days
            employee.save()

        elif action == 'reject':
            leave.status = 'Rejected'
            leave.rejection_reason = request.POST.get('rejection_reason')

        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()

        messages.success(request, f"Leave {leave.status.lower()} successfully")

    return redirect('admin_leave_list')


# ================= ATTENDANCE =================


@login_required
def employee_attendance_history(request):
    employee = request.user.employee_profile

    attendances = Attendance.objects.filter(employee=employee)
    leaves = Leave.objects.filter(employee=employee, status='Approved')
    holidays = Holiday.objects.all()

    rows = {}

    # Attendance
    for att in attendances:
        rows[att.date] = {
            'date': att.date,
            'punch_in': att.punch_in,
            'punch_out': att.punch_out,
            'working_hours': att.working_hours,
            'status': att.status
        }

    # Leave override
    for leave in leaves:
        current = leave.start_date
        while current <= leave.end_date:
            rows[current] = {
                'date': current,
                'punch_in': None,
                'punch_out': None,
                'working_hours': None,
                'status': 'Leave'
            }
            current += timedelta(days=1)

    # Holiday (only if no attendance or leave)
    for holiday in holidays:
        if holiday.date not in rows:
            rows[holiday.date] = {
                'date': holiday.date,
                'punch_in': None,
                'punch_out': None,
                'working_hours': None,
                'status': 'Holiday'
            }

    history = sorted(rows.values(), key=lambda x: x['date'], reverse=True)

    events = get_calendar_events(employee)

    return render(
        request,
        'employee/attendance_history.html',  # ← make sure this matches template
        {
            'history': history,
            'events': json.dumps(events)
        }
    )


# ================= PUNCH IN =================


@login_required
def punch_in(request):
    if request.method != "POST":
        return redirect('employee_dashboard')

    employee = request.user.employee_profile
    today = timezone.localdate()
    now_time = timezone.localtime().time()

    # 🔹 Check approved leave
    if Leave.objects.filter(
        employee=employee,
        start_date__lte=today,
        end_date__gte=today,
        status='Approved'
    ).exists():
        messages.error(request, "You are on approved leave today.")
        return redirect('employee_dashboard')

    # 🔹 Get active shift
    shift_assignment = ShiftAssignment.objects.filter(
        employee=employee,
        is_active=True
    ).select_related('shift').first()

    if not shift_assignment:
        messages.error(request, "No shift assigned. Contact HR.")
        return redirect('employee_dashboard')

    shift = shift_assignment.shift

    # 🔹 Punch-in time window
    shift_start_dt = datetime.combine(today, shift.start_time)

    early_limit = shift_start_dt - timedelta(
        minutes=settings.PUNCH_EARLY_MINUTES
    )
    late_limit = shift_start_dt + timedelta(
        minutes=settings.PUNCH_LATE_MINUTES
    )

    now_dt = datetime.combine(today, now_time)

    if not (early_limit <= now_dt <= late_limit):
        messages.error(request, "Punch-in not allowed at this time.")
        return redirect('employee_dashboard')

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )

    if attendance.punch_in:
        messages.warning(request, "You have already punched in today.")
        return redirect('employee_dashboard')

    attendance.punch_in = timezone.now()

    # 🔹 Late calculation (shift-based)
    grace_dt = shift_start_dt + timedelta(
        minutes=settings.SHIFT_GRACE_MINUTES
    )

    if now_dt > grace_dt:
        attendance.status = 'Late'
    else:
        attendance.status = 'Present'

    attendance.save()
    messages.success(request, "Punch in successful.")

    return redirect('employee_dashboard')
    
# ================= PUNCH OUT =================


@login_required
def punch_out(request):
    if request.method != "POST":
        return redirect('employee_dashboard')

    employee = request.user.employee_profile
    today = timezone.localdate()

    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, "You must punch in first.")
        return redirect('employee_dashboard')

    if attendance.punch_out:
        messages.warning(request, "You have already punched out today.")
        return redirect('employee_dashboard')

    attendance.punch_out = timezone.now()

    # ✅ Use stored datetimes directly
    in_dt = attendance.punch_in
    out_dt = attendance.punch_out

    # ✅ Night shift handling
    shift_assignment = ShiftAssignment.objects.filter(
        employee=employee,
        is_active=True
    ).select_related('shift').first()

    if shift_assignment:
        shift = shift_assignment.shift
        is_night_shift = shift.end_time < shift.start_time

        if is_night_shift and out_dt < in_dt:
            out_dt += timedelta(days=1)

    # ✅ Working hours calculation
    diff = out_dt - in_dt
    hours = round(diff.total_seconds() / 3600, 2)
    attendance.working_hours = Decimal(str(hours))

    # ✅ Half-day rule
    if hours < settings.MIN_HALF_DAY_HOURS:
        attendance.status = 'Half Day'

    attendance.save()
    messages.success(request, "Punch out successful.")

    return redirect('employee_dashboard')

def mark_absent_for_today():
    today = timezone.localdate()

    employees = Employee.objects.filter(is_active=True)

    for emp in employees:
        # Skip if approved leave
        if Leave.objects.filter(
            employee=emp,
            start_date__lte=today,
            end_date__gte=today,
            status='Approved'
        ).exists():
            continue

        attendance, created = Attendance.objects.get_or_create(
            employee=emp,
            date=today
        )

        if not attendance.punch_in and not attendance.punch_out:
            attendance.status = 'Absent'
            attendance.save()
            
            
def get_calendar_events(employee):
    events = {}
    
    color_map = {
        'Present': '#198754',
        'Late': '#ffc107',
        'Half Day': '#212529',
        'Absent': '#dc3545',
        'Leave': '#0dcaf0',
        'Holiday': '#0FF845',
        'Sunday': '#6c757d',
    }

    # -----------------------
    # 1️⃣ Attendance (Highest Priority)
    # -----------------------
    attendances = Attendance.objects.filter(employee=employee)
    for att in attendances:
        events[str(att.date)] = {
            'title': att.status,
            'start': att.date.strftime('%Y-%m-%d'),
            'color': color_map.get(att.status),
            'extendedProps': {
                'punch_in': att.punch_in.strftime('%I:%M %p') if att.punch_in else '-',
                'punch_out': att.punch_out.strftime('%I:%M %p') if att.punch_out else '-',
                'working_hours': float(att.working_hours) if att.working_hours else 0,
                'status': att.status,
            }
        }

    # -----------------------
    # 2️⃣ Approved Leave (Override Attendance)
    # -----------------------
    leaves = Leave.objects.filter(employee=employee, status='Approved')
    for leave in leaves:
        current = leave.start_date
        while current <= leave.end_date:
            events[str(current)] = {
                'title': 'Leave',
                'start': current.strftime('%Y-%m-%d'),
                'color': color_map['Leave'],
                'extendedProps': {'status': 'Leave'}
            }
            current += timedelta(days=1)

    # -----------------------
    # 3️⃣ Holidays (Only if not already marked)
    # -----------------------
    holidays = Holiday.objects.all()
    for holiday in holidays:
        key = str(holiday.date)
        if key not in events:
            events[key] = {
                'title': f"Holiday - {holiday.name}",
                'start': holiday.date.strftime('%Y-%m-%d'),
                'color': color_map['Holiday'],
                'extendedProps': {'status': 'Holiday'}
            }

    # -----------------------
    # 4️⃣ Sundays (Auto Weekly Off)
    # -----------------------
    today = date.today()
    year = today.year

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    current = start_date
    while current <= end_date:
        if current.weekday() == 6:  # Sunday
            key = str(current)
            if key not in events:
                events[key] = {
                    'title': 'Sunday',
                    'start': current.strftime('%Y-%m-%d'),
                    'color': color_map['Sunday'],
                    'extendedProps': {'status': 'Sunday'}
                }
        current += timedelta(days=1)

    return list(events.values())


@staff_member_required
def admin_employee_attendance_list(request):
    employees = Employee.objects.all().order_by('employee_id')
    return render(
        request,
        'admin/attendance/employee_list.html',
        {'employees': employees}
    )

@staff_member_required
def admin_employee_attendance_detail(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)

    attendances = Attendance.objects.filter(employee=employee)
    leaves = Leave.objects.filter(employee=employee, status='Approved')
    holidays = Holiday.objects.all()

    rows = {}

    # 1️⃣ Attendance (Highest priority)
    for att in attendances:
        rows[att.date] = {
            'date': att.date,
            'punch_in': att.punch_in,
            'punch_out': att.punch_out,
            'working_hours': att.working_hours,
            'status': att.status
        }

    # 2️⃣ Leave (Override Attendance)
    for leave in leaves:
        current = leave.start_date
        while current <= leave.end_date:
            rows[current] = {
                'date': current,
                'punch_in': None,
                'punch_out': None,
                'working_hours': None,
                'status': 'Leave'
            }
            current += timedelta(days=1)

    # 3️⃣ Holidays (Only if not already marked)
    for holiday in holidays:
        if holiday.date not in rows:
            rows[holiday.date] = {
                'date': holiday.date,
                'punch_in': None,
                'punch_out': None,
                'working_hours': None,
                'status': 'Holiday'
            }

    # 4️⃣ Sundays (Only if not already marked)
    start_date = date.today().replace(month=1, day=1)
    end_date = date.today()

    current = start_date
    while current <= end_date:
        if current.weekday() == 6:  # Sunday
            if current not in rows:
                rows[current] = {
                    'date': current,
                    'punch_in': None,
                    'punch_out': None,
                    'working_hours': None,
                    'status': 'Sunday'
                }
        current += timedelta(days=1)

    history = sorted(rows.values(), key=lambda x: x['date'], reverse=True)

    return render(
        request,
        'admin/attendance/employee_attendance_detail.html',
        {
            'employee': employee,
            'history': history
        }
    )



@staff_member_required
def admin_employee_attendance_calendar(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    events = get_calendar_events(employee)

    return render(
        request,
        'admin/attendance/employee_calendar.html',
        {'employee': employee, 'events': events}
    )


@login_required
def process_attendance_view(request):

    employees = Employee.objects.all().order_by('employee_id')
    today = localdate()

    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    emp_id = request.GET.get('employee_id')

    selected_employee = None
    records = Attendance.objects.none()
    summary = None
    processed = False

    # =====================
    # PROCESS ATTENDANCE
    # =====================
    if request.method == "POST":

        emp_id = request.POST.get("employee_id")
        month = request.POST.get("month")
        year = request.POST.get("year")

        employee = Employee.objects.get(id=emp_id)

        Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        ).update(is_processed=True)

        messages.success(request, "Attendance processed successfully and locked.")

        return redirect(
            f"/attendance/process/?employee_id={emp_id}&month={month}&year={year}"
        )

    # =====================
    # DISPLAY DATA
    # =====================
    if emp_id:

        selected_employee = Employee.objects.get(id=emp_id)

        records = Attendance.objects.filter(
            employee=selected_employee,
            date__year=selected_year,
            date__month=selected_month
        )

        # check if already processed
        if records.exists():
            processed = records.filter(is_processed=True).exists()

        # =====================
        # LEAVE CALCULATION
        # =====================

        lwp_assigned = settings.PL_LIMIT_PER_MONTH

        leave_days = 0

        leaves = Leave.objects.filter(
            employee=selected_employee,
            status='Approved'
        )

        for leave in leaves:
            current = leave.start_date

            while current <= leave.end_date:

                if current.year == selected_year and current.month == selected_month:
                    leave_days += 1

                current += timedelta(days=1)

        lwp_used = leave_days
        lwp_remaining = lwp_assigned - lwp_used

        summary = {
            'working_days': get_working_days_of_month(selected_year, selected_month),

            'present_days': records.filter(
                status__in=['Present', 'Late']
            ).count(),

            'absent_days': records.filter(
                status='Absent'
            ).count(),

            'lwp_assigned': lwp_assigned,
            'lwp_used': lwp_used,
            'lwp_remaining': lwp_remaining,
        }

    context = {
        'employees': employees,
        'selected_employee': selected_employee,
        'records': records,
        'processed': processed,
        'summary': summary,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': list(enumerate(calendar.month_name))[1:],
        'years': range(today.year - 1, today.year + 4),
    }

    return render(request, 'attendance/process_attendance.html', context)


@login_required
def apply_regularization(request, date):
    employee = request.user.employee_profile

    attendance = Attendance.objects.filter( 
        employee=employee,
        date=date
    ).first()

    if not attendance:
        attendance = Attendance.objects.create(
            employee=employee,
            date=date
        )

    if request.method == "POST":
        AttendanceRegularization.objects.create(
            employee=employee,
            attendance=attendance,
            requested_punch_in=request.POST.get("punch_in") or None,
            requested_punch_out=request.POST.get("punch_out") or None,
            requested_status=request.POST.get("status"),
            reason=request.POST.get("reason")
        )

        messages.success(request, "Request submitted successfully.")
        return redirect("employee_attendance_history")

    return render(request, "attendance/apply_regularization.html", {
        "attendance": attendance
    })

@staff_member_required
def admin_regularization_list(request):
    requests = AttendanceRegularization.objects.all().order_by('-applied_at')

    return render(
        request,
        'admin/attendance/regularization_list.html',
        {'requests': requests}
    )
@staff_member_required
def admin_regularization_action(request, pk, action):
    reg = get_object_or_404(AttendanceRegularization, pk=pk)

    if reg.status == "Pending":

        if action == "approve":
            attendance = reg.attendance

            if reg.requested_punch_in:
                attendance.punch_in = reg.requested_punch_in

            if reg.requested_punch_out:
                attendance.punch_out = reg.requested_punch_out

            if reg.requested_status:
                attendance.status = reg.requested_status

            attendance.save()

            reg.status = "Approved"

        elif action == "reject":
            reg.status = "Rejected"

        reg.reviewed_by = request.user
        reg.reviewed_at = timezone.now()
        reg.save()

    return redirect('admin_regularization_list')

@login_required
def generate_salary_page(request):

    departments = Department.objects.all()
    employees = None

    dept_id = request.GET.get("department")

    if dept_id:
        employees = Employee.objects.filter(department_id=dept_id)

    return render(request, "salary/generate_salary.html", {
        "departments": departments,
        "employees": employees
    })

@login_required
def run_salary_generation(request):

    if request.method == "POST":

        department = request.POST.get("department")
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))

        employee_ids = request.POST.getlist("employee_ids")

        for emp_id in employee_ids:

            emp = Employee.objects.get(id=emp_id)

            basic = float(request.POST.get(f"basic_{emp_id}", 0))
            hra = float(request.POST.get(f"hra_{emp_id}", 0))
            allowance = float(request.POST.get(f"allowance_{emp_id}", 0))

            generate_salary(emp, month, year, basic, hra, allowance)

        messages.success(request, "Salary generated successfully")

        return redirect("generate_salary_page")