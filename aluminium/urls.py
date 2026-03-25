from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),

    # Department
    path('department/', views.department_list, name='department_list'),
    path('department/add/', views.department_add, name='department_add'),
    path('department/edit/<int:pk>/', views.department_edit, name='department_edit'),
    path('department/delete/<int:pk>/', views.department_delete, name='department_delete'),

    # Designation
    path('designation/', views.designation_list, name='designation_list'),
    path('designation/add/', views.designation_add, name='designation_add'),
    path('designation/edit/<int:pk>/', views.designation_edit, name='designation_edit'),
    path('designation/delete/<int:pk>/', views.designation_delete, name='designation_delete'),

    # Employee
    path('employee/', views.employee_list, name='employee_list'),
    path('employee/add/', views.employee_add, name='employee_add'),
    path('employee/view/<int:pk>/', views.employee_view, name='employee_view'),
    path('employee/edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('employee/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('employee/toggle-status/<int:pk>/', views.employee_toggle_status, name='employee_toggle_status'),

    # Shift
    path('shift/', views.shift_list, name='shift_list'),
    path('shift/add/', views.shift_add, name='shift_add'),
    path('shift/edit/<int:pk>/', views.shift_edit, name='shift_edit'),
    path('shift/toggle/<int:pk>/', views.shift_toggle_status, name='shift_toggle_status'),

    # Shift Assignment
    path('shift-assign/', views.shift_assign, name='shift_assign'),
    path('shift-assign/list/', views.shift_assign_list, name='shift_assign_list'),
    path('shift-assign/edit/<int:pk>/', views.shift_assign_edit, name='shift_assign_edit'),

    # AJAX
    path('ajax/employees/all/', views.get_all_employees, name='get_all_employees'),
    
    # Employee Leave
    path('employee/leave/apply/', views.apply_leave, name='apply_leave'),
    path('employee/leaves/', views.my_leaves, name='my_leaves'),

    # Admin Leave
    path('leave/manage/', views.admin_leave_list, name='admin_leave_list'),
    path('leave/manage/<int:pk>/<str:action>/', views.admin_leave_action, name='admin_leave_action'),
    
    # urls.py
    path('employee/profile/', views.employee_profile, name='employee_profile'),

    path('attendance/my/',views.employee_attendance_history,name='employee_attendance_history'),
    path('attendance/punch-in/',views.punch_in,name='punch_in'),
    path('attendance/punch-out/',views.punch_out,name='punch_out'),
    path('dashboard/attendance/employees/',views.admin_employee_attendance_list,name='admin_employee_attendance_list'),
    path('dashboard/attendance/employee/<int:emp_id>/',views.admin_employee_attendance_detail,name='admin_employee_attendance_detail'),

    path('dashboard/attendance/calendar/<int:emp_id>/',views.admin_employee_attendance_calendar,name='admin_employee_attendance_calendar'),
    path('employee/shift/',views.employee_shift_details,name='employee_shift_details'),

    path('attendance/process/', views.process_attendance_view, name='process_attendance'),
    path("attendance/processed/",views.processed_attendance_list,name="processed_attendance_list"),
    path("attendance/processed/<int:emp_id>/",views.processed_attendance_detail,name="processed_attendance_detail"),
    path("salary/attendance-summary/<int:emp_id>/",views.salary_attendance_summary,name="salary_attendance_summary"),
    path("salary/generate-single/",views.generate_single_salary,name="generate_single_salary"),
    path('attendance/regularize/<str:date>/', views.apply_regularization, name='apply_regularization'),
    path('dashboard/regularization/', views.admin_regularization_list, name='admin_regularization_list'),
    path('dashboard/regularization/<int:pk>/<str:action>/', views.admin_regularization_action, name='admin_regularization_action'),

    path('salary/generate/', views.generate_salary_page, name='generate_salary_page'),
    path('salary/run/', views.run_salary_generation, name='run_salary_generation'),
    path('accounts/generate-salary/', views.generate_salary_page, name='accounts_generate_salary'),
    path('salary/list/', views.salary_list, name='salary_list'),
    path("employee/salary/",views.employee_salary_list,name="employee_salary_list"),
    path("payslip/<int:salary_id>/",views.payslip_view,name="payslip_view"),
    path("hr/dashboard/",views.hr_dashboard,name="hr_dashboard"),
    path('accounts/dashboard/', views.accounts_dashboard, name='accounts_dashboard'),
    path('accounts/salaries/', views.accounts_salary_list, name='accounts_salary_list'),
    path('accounts/payslip/<int:salary_id>/', views.accounts_payslip_view, name='accounts_payslip'),
    path('performance/', include('performance.urls')),
    path('inventory/', include('inventory.urls')),
    path('', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
