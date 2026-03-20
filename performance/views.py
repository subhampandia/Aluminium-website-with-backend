from django.shortcuts import render, redirect
from .models import Goal,PerformanceReview
from app.models import Employee
from .forms import GoalForm,ReviewForm
from django.contrib.auth.decorators import user_passes_test

def is_hr(user):
    return user.is_authenticated and Employee.objects.filter(user=user, role='HR').exists()

@user_passes_test(is_hr)
def goal_list(request):
    goals = Goal.objects.all()
    return render(request, 'performance/goal_list.html', {'goals': goals})


@user_passes_test(is_hr)
def add_goal(request):
    form = GoalForm(request.POST or None)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.created_by = request.user.employee   # HR user
        goal.save()
        return redirect('goal_list')
    return render(request, 'performance/add_goal.html', {'form': form})

@user_passes_test(is_hr)
def review_list(request):
    reviews = PerformanceReview.objects.all()
    return render(request, 'performance/review_list.html', {'reviews': reviews})


@user_passes_test(is_hr)
def add_review(request):
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.reviewer = Employee.objects.get(user=request.user)
        review.save()
        return redirect('review_list')
    return render(request, 'performance/add_review.html', {'form': form})