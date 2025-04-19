from django import forms
from .models import InvestmentOpportunity

class FundUpdateForm(forms.Form):
    amount = forms.FloatField(label='Add Fund (৳)', min_value=0)


class InvestmentOpportunityForm(forms.ModelForm):
    
    class Meta:
        model = InvestmentOpportunity
        fields = ['title', 'description', 'amount_required', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter opportunity title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Provide a description', 'rows': 4}),
            'amount_required': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount required'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

from django import forms
from .models import MemberFinance  # make sure this is your correct model

class MemberFinanceForm(forms.ModelForm):
    class Meta:
        model = MemberFinance
        fields = ['total_fund', 'total_income', 'total_expense']  # or other fields you want editable
        widgets = {
            'total_fund': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_expense': forms.NumberInput(attrs={'class': 'form-control'}),
        }
