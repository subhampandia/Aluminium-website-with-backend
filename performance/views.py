from django.shortcuts import render, redirect
from .models import Goal,PerformanceReview
from app.models import Employee
from .forms import GoalForm,ReviewForm
from django.contrib.auth.decorators import user_passes_test
def is_employee(user):
    return user.is_authenticated and Employee.objects.filter(user=user).exists()
def is_hr_or_admin(user):
    if not user.is_authenticated:
        return False

    # Admin always allowed
    if user.is_superuser:
        return True

    # HR allowed
    return Employee.objects.filter(user=user, role='HR').exists()

def get_base_template(user):
    if user.is_superuser:
        return 'base_dashboard.html'   # your admin base
    else:
        return 'base_hr_dashboard.html'
    
    
@user_passes_test(is_hr_or_admin)
def goal_list(request):
    goals = Goal.objects.all()
    base_template = get_base_template(request.user)
    return render(request, 'performance/goal_list.html', {'goals': goals,'base_template': base_template})

@user_passes_test(is_hr_or_admin)
def add_goal(request):
    base_template = get_base_template(request.user)

    if request.method == "POST":
        form = GoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)

            employee = Employee.objects.filter(user=request.user).first()
            goal.created_by = employee
            goal.created_by_user = request.user
            
            goal.save()
            return redirect('goal_list')
        else:
            print("FORM ERRORS ❌:", form.errors)
    else:
        form = GoalForm()

    return render(request, 'performance/add_goal.html', {
        'form': form,
        'base_template': base_template
    })

@user_passes_test(is_hr_or_admin)
def review_list(request):
    reviews = PerformanceReview.objects.all()
    base_template = get_base_template(request.user)
    return render(request, 'performance/review_list.html', {'reviews': reviews,'base_template': base_template})


@user_passes_test(is_hr_or_admin)
def add_review(request):
    base_template = get_base_template(request.user)
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        employee = Employee.objects.filter(user=request.user).first()
        review.reviewer = employee
        review.save()
        return redirect('review_list')
    return render(request, 'performance/add_review.html', {'form': form,'base_template': base_template})

@user_passes_test(is_employee)
def my_tasks(request):
    employee = Employee.objects.filter(user=request.user).first()
    tasks = Goal.objects.filter(employee=employee)

    base_template = get_base_template(request.user)

    return render(request, 'performance/my_tasks.html', {
        'tasks': tasks,
        'base_template': base_template
    })
    
@user_passes_test(is_employee)
def accept_task(request, pk):
    employee = Employee.objects.filter(user=request.user).first()

    task = Goal.objects.filter(id=pk, employee=employee).first()  # ✅ secure

    if task and task.status == 'Assigned':
        task.status = 'In Progress'
        task.save()

    return redirect('my_tasks')

@user_passes_test(is_employee)
def complete_task(request, pk):
    employee = Employee.objects.filter(user=request.user).first()

    task = Goal.objects.filter(id=pk, employee=employee).first()  # ✅ secure

    if task and task.status == 'In Progress':
        task.status = 'Completed'
        task.save()

    return redirect('my_tasks')