from django.utils.timezone import localdate
from app.models import Leave,Attendance,MonthlySalary


def get_used_pl(employee, date=None):
    """
    Counts approved PL (Leave With Pay) used in the given month
    """
    if date is None:
        date = localdate()

    return Leave.objects.filter(
        employee=employee,
        leave_type='PL',        # PL = Leave With Pay
        status='Approved',
        start_date__year=date.year,
        start_date__month=date.month
    ).count()

from django.conf import settings

def resolve_leave_status(employee, leave_date):
    """
    Decides final attendance status for a PL (Leave With Pay) day.
    """
    used_pl = get_used_pl(employee, leave_date)

    if used_pl <= settings.PL_LIMIT_PER_MONTH:
        return 'LWP'       # Leave With Pay (PAID)
    else:
        return 'Absent'   # Exceeded limit → NO PAY


import calendar
from datetime import date
from app.models import Holiday   # adjust app name if needed


def get_working_days_of_month(year, month):
    """
    Returns number of working days in a month
    (Excludes Sundays and public holidays)
    """
    total_days = calendar.monthrange(year, month)[1]

    # Get all holiday dates for the month
    holidays = set(
        Holiday.objects.filter(
            date__year=year,
            date__month=month
        ).values_list('date', flat=True)
    )

    working_days = 0

    for day in range(1, total_days + 1):
        current_date = date(year, month, day)

        # ❌ Exclude Sundays (Monday=0, Sunday=6)
        if current_date.weekday() == 6:
            continue

        # ❌ Exclude public holidays
        if current_date in holidays:
            continue

        working_days += 1

    return working_days

def generate_salary(employee, month, year, basic, hra, allowance):

    gross = basic + hra + allowance
    records = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        is_processed=True
    )

    absent_days = records.filter(status='Absent').count()
    leave_days = records.filter(status="Leave").count()
    half_days = records.filter(status='Half Day').count()

    pl_limit = settings.PL_LIMIT_PER_MONTH

    extra_leave_days = max(0, leave_days - pl_limit)


    total_deduction_days = absent_days + extra_leave_days + (half_days * 0.5)
    
    working_days = get_working_days_of_month(year, month)
    per_day_basic = basic / working_days if working_days else 0

    present_days = records.filter(
        status__in=["Present","Late","Half Day"]).count()

    leave_deduction = total_deduction_days * per_day_basic

    emp_pf = basic * 0.12
    employer_pf = basic * 0.12

    emp_esic = gross * 0.0075
    employer_esic = gross * 0.0325

    net_salary = gross - leave_deduction - emp_pf - emp_esic

    MonthlySalary.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={
            "working_days": working_days,
            "present_days": present_days,
            "half_days": half_days,
            "gross_salary": gross,
            "absent_days": absent_days,
            "extra_leave_days": extra_leave_days,
            "leave_deduction": leave_deduction,
            "emp_pf": emp_pf,
            "employer_pf": employer_pf,
            "emp_esic": emp_esic,
            "employer_esic": employer_esic,
            "net_salary": net_salary
        }
    )