from django.utils.timezone import localdate
from app.models import Leave


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
