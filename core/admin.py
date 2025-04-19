from django.contrib import admin
from .models import InvestmentOpportunity, Vote

admin.site.register(InvestmentOpportunity)
admin.site.register(Vote)


# core/admin.py

from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__username', 'message')


