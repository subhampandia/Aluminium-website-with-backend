"""
URL configuration for aluminium project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app.views import *
    
# from app.views import (
#     index,
#     login_view,
#     logout_view,
#     dashboard,
#     department_list,
#     department_add,
#     department_edit,
#     department_delete,
# )
# from app.views import (
#     designation_list,
#     designation_add,
#     designation_edit,
#     designation_delete,
# )

# from app.views import (
#     employee_list,
#     employee_add,
#     employee_view,
#     employee_edit,
#     employee_delete,employee_toggle_status  
# )
# from app.views import(
#     shift_list,
#     shift_add,
#     shift_edit,
#     shift_toggle_status
# )
# from app.views import (
#     shift_assign,
#     shift_assign_list,
#     get_employees_by_department
# )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

    path('department/', department_list, name='department_list'),
    path('department/add/', department_add, name='department_add'),
    path('department/edit/<int:pk>/', department_edit, name='department_edit'),
    path('department/delete/<int:pk>/', department_delete, name='department_delete'),

    path('designation/', designation_list, name='designation_list'),
    path('designation/add/', designation_add, name='designation_add'),
    path('designation/edit/<int:pk>/', designation_edit, name='designation_edit'),
    path('designation/delete/<int:pk>/', designation_delete, name='designation_delete'),

    path('employee/', employee_list, name='employee_list'),
    path('employee/add/', employee_add, name='employee_add'),
    path('employee/view/<int:pk>/', employee_view, name='employee_view'),
    path('employee/edit/<int:pk>/', employee_edit, name='employee_edit'),
    path('employee/delete/<int:pk>/', employee_delete, name='employee_delete'),
    path('employee/toggle-status/<int:pk>/', employee_toggle_status, name='employee_toggle_status'),

    path('shift/', shift_list, name='shift_list'),
    path('shift/add/', shift_add, name='shift_add'),    
    path('shift/edit/<int:pk>/', shift_edit, name='shift_edit'),
    path('shift/toggle/<int:pk>/', shift_toggle_status, name='shift_toggle_status'),
    
    path('shift-assign/', shift_assign, name='shift_assign'),
    path('shift-assign/list/', shift_assign_list, name='shift_assign_list'),
    path('ajax/employees/all/', get_all_employees, name='get_all_employees'),
    path('shift-assign/edit/<int:pk>/',shift_assign_edit,name='shift_assign_edit'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

