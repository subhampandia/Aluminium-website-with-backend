from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from app.models import Employee, Attendance, Leave, ShiftAssignment, Holiday

class Command(BaseCommand):
    help = "Mark absent (shift, weekly off, holiday aware)"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        today = timezone.localdate()

        for emp in Employee.objects.filter(is_active=True):

            # 1️⃣ Approved leave
            if Leave.objects.filter(
                employee=emp,
                start_date__lte=today,
                end_date__gte=today,
                status='Approved'
            ).exists():
                self._mark(emp, today, 'Leave')
                continue

            # 2️⃣ Holiday
            if Holiday.objects.filter(date=today).exists():
                self._mark(emp, today, 'Holiday')
                continue

            # 3️⃣ Get active shift FIRST
            assignment = ShiftAssignment.objects.filter(
                employee=emp,
                is_active=True
            ).select_related('shift').first()

            if not assignment:
                continue  # no shift assigned → skip safely

            shift = assignment.shift  # ✅ NOW shift exists

            # 4️⃣ Weekly off (shift-based)
            if shift.weekly_off == today.strftime('%A'):
                self._mark(emp, today, 'Holiday')
                continue

            # 5️⃣ Shift end time
            shift_end = datetime.combine(today, shift.end_time)

            # 🌙 Night shift
            if shift.end_time < shift.start_time:
                shift_end += timedelta(days=1)

            # Grace buffer
            shift_end += timedelta(minutes=5)

            # Make timezone-aware
            shift_end = timezone.make_aware(shift_end)

            # Too early → skip
            if now < shift_end:
                continue

            # 6️⃣ Attendance check
            attendance = Attendance.objects.filter(
                employee=emp,
                date=today
            ).first()

            # No record → Absent
            if not attendance:
                Attendance.objects.create(
                    employee=emp,
                    date=today,
                    status='Absent'
                )
                continue

            # Record exists but no punches → Absent
            if not attendance.punch_in and not attendance.punch_out:
                attendance.status = 'Absent'
                attendance.save()

    def _mark(self, emp, day, status):
        attendance, _ = Attendance.objects.get_or_create(
            employee=emp,
            date=day
        )
        attendance.status = status
        attendance.save()
