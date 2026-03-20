from django import forms
from .models import Goal,PerformanceReview

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        exclude = ['reviewer']
        fields = '__all__'