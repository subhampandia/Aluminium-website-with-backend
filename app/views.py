from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
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

@never_cache
@login_required(login_url='login')
def department_list(request):
    departments = Department.objects.all().order_by('id')
    return render(request, 'department/department_list.html', {
        'departments': departments
    })


@login_required(login_url='login')
def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            Department.objects.create(
                name=name,
                description=description
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

    return render(request, 'department/department_edit.html', {
        'department': department
    })


@login_required(login_url='login')
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.delete()
    messages.success(request, "Department deleted successfully")
    return redirect('department_list')
