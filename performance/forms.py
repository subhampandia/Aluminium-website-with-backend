from django import forms
from .models import Goal,PerformanceReview

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        exclude = ['achieved_value', 'created_by']
        fields = '__all__'
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        exclude = ['reviewer']
        fields = '__all__'
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class TaskSubmitForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['submitted_at']
        widgets = {
            'submitted_at': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }