from django.db import models
from django.contrib.auth.models import User
import datetime

class MemberFinance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_fund = models.FloatField(default=0.0)
    total_income = models.FloatField(default=0.0)
    total_expense = models.FloatField(default=0.0)

    def net_profit(self):
        return self.total_income - self.total_expense

class MonthlyBreakdown(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    income = models.FloatField(default=0)
    expense = models.FloatField(default=0)


from django.db import models

class InvestmentOpportunity(models.Model):
    title = models.CharField(max_length=200)  # 'name' এর জায়গায় 'title'
    description = models.TextField()
    amount_required = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    deadline = models.DateField(default=datetime.date(2025, 12, 31))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title 



# class Vote(models.Model):
#     opportunity = models.ForeignKey(InvestmentOpportunity, on_delete=models.CASCADE)
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#     vote = models.BooleanField()  # True = Yes, False = No

#     def __str__(self):
#         return f"{self.user.username} - {'Yes' if self.vote else 'No'}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(InvestmentOpportunity, on_delete=models.CASCADE)
    vote = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    change_count = models.IntegerField(default=0)  # Tracks how many times vote changed

    class Meta:
        unique_together = ('user', 'opportunity')



class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.user.username}"


# core/models.py

# class Fund(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - ৳{self.amount}"


class Fund(models.Model):
    CATEGORY_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('profit', 'Profit'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    date = models.DateField(auto_now_add=True)
