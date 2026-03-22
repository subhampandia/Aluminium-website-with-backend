from django.urls import path
from . import views

urlpatterns = [
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('task/accept/<int:pk>/', views.accept_task, name='accept_task'),
    path('task/complete/<int:pk>/', views.complete_task, name='complete_task'),
]