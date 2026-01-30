from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
