from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Employee, Attendance, Leave

class Command(BaseCommand):
    help = "Mark absent only if no punch-in and no punch-out"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        for emp in Employee.objects.filter(is_active=True):

            # 🔹 Skip if approved leave
            if Leave.objects.filter(
                employee=emp,
                start_date__lte=today,
                end_date__gte=today,
                status='Approved'
            ).exists():
                continue

            attendance = Attendance.objects.filter(
                employee=emp,
                date=today
            ).first()

            # 🔹 Case 1: No attendance record at all
            if not attendance:
                Attendance.objects.create(
                    employee=emp,
                    date=today,
                    status='Absent'
                )
                continue

            # 🔹 Case 2: Attendance exists but no punch in & out
            if not attendance.punch_in and not attendance.punch_out:
                attendance.status = 'Absent'
                attendance.save()
