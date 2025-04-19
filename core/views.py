from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import FileResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from django.utils import timezone

from .models import MemberFinance, MonthlyBreakdown, InvestmentOpportunity, Vote, Testimonial, Fund
from .forms import FundUpdateForm, InvestmentOpportunityForm, MemberFinanceForm

# -------------------- HOME VIEW --------------------
def home(request):
    total_fund = Fund.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = Fund.objects.filter(category='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Fund.objects.filter(category='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    next_opportunity = InvestmentOpportunity.objects.filter(deadline__gte=timezone.now()).order_by('deadline').first()
    testimonials = Testimonial.objects.all()

    chart_data = generate_sample_chart_data()

    return render(request, 'core/home.html', {
        "total_fund": total_fund,
        "total_income": total_income,
        "total_expense": total_expense,
        "next_opportunity": next_opportunity,
        "testimonials": testimonials,
        "chart_data": chart_data
    })


# -------------------- DASHBOARD --------------------
@login_required
def dashboard(request):
    total_firm_fund = MemberFinance.objects.aggregate(Sum('total_fund'))['total_fund__sum'] or 0
    all_finances = MemberFinance.objects.all() if request.user.is_staff else None

    finance = MemberFinance.objects.get(user=request.user)
    breakdowns = MonthlyBreakdown.objects.filter(user=request.user)

    users = User.objects.all() if request.user.is_staff else None
    selected_user_id = request.GET.get('user_id')

    if request.user.is_staff and selected_user_id:
        selected_user = get_object_or_404(User, id=selected_user_id)
        finance = MemberFinance.objects.get(user=selected_user)
        breakdowns = MonthlyBreakdown.objects.filter(user=selected_user)

    form = FundUpdateForm(request.POST or None)

    if request.method == 'POST' and request.user.is_staff:
        if form.is_valid():
            amount = form.cleaned_data['amount']
            finance.total_fund += amount
            finance.save()
            messages.success(request, f"৳{amount} added to {finance.user.username}'s fund successfully!")
            return redirect('dashboard')

    return render(request, 'core/dashboard.html', {
        'finance': finance,
        'breakdowns': breakdowns,
        'form': form,
        'users': users,
        'selected_user_id': selected_user_id,
        'all_finances': all_finances,
        'total_firm_fund': total_firm_fund,
    })


# -------------------- ADMIN SUMMARY --------------------
@staff_member_required
def admin_summary(request):
    query = request.GET.get('q')
    finances = MemberFinance.objects.all()

    if query:
        finances = finances.filter(Q(user__username__icontains=query))

    return render(request, 'core/admin_summary.html', {
        'finances': finances,
        'query': query
    })


# -------------------- PDF DOWNLOAD --------------------
@login_required
def download_report(request):
    finance = MemberFinance.objects.get(user=request.user)
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Monthly Report - {request.user.username}")
    p.drawString(100, 780, f"Total Fund: ৳{finance.total_fund}")
    p.drawString(100, 760, f"Total Income: ৳{finance.total_income}")
    p.drawString(100, 740, f"Total Expense: ৳{finance.total_expense}")
    p.drawString(100, 720, f"Net Profit: ৳{finance.net_profit()}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='report.pdf')


# -------------------- OPPORTUNITIES --------------------
@login_required
def opportunities(request):
    all_opportunities = InvestmentOpportunity.objects.all()
    user_votes = {v.opportunity_id: v.vote for v in Vote.objects.filter(user=request.user)}

    vote_counts = {}
    for opp in all_opportunities:
        yes_count = Vote.objects.filter(opportunity=opp, vote='yes').count()
        no_count = Vote.objects.filter(opportunity=opp, vote='no').count()
        total = yes_count + no_count
        yes_percent = int((yes_count / total) * 100) if total > 0 else 0
        no_percent = 100 - yes_percent if total > 0 else 0

        vote_counts[opp.id] = {
            'yes': yes_count,
            'no': no_count,
            'yes_percent': yes_percent,
            'no_percent': no_percent,
        }

    return render(request, 'core/opportunities.html', {
        'opportunities': all_opportunities,
        'user_votes': user_votes,
        'vote_counts': vote_counts,
    })


# -------------------- VOTING --------------------
@login_required
def vote_opportunity(request, opportunity_id, vote_choice):
    opportunity = get_object_or_404(InvestmentOpportunity, id=opportunity_id)
    vote_obj, created = Vote.objects.get_or_create(user=request.user, opportunity=opportunity)

    if created:
        vote_obj.vote = vote_choice
        vote_obj.save()
        messages.success(request, "Your vote has been recorded.")
    elif vote_obj.vote == vote_choice:
        messages.info(request, "You already voted this option.")
    elif vote_obj.change_count < 2:
        vote_obj.vote = vote_choice
        vote_obj.change_count += 1
        vote_obj.save()
        messages.success(request, f"Your vote has been changed ({vote_obj.change_count}/2).")
    else:
        messages.error(request, "You’ve reached the maximum number of vote changes (2).")

    return redirect('opportunities')


@login_required
def unvote_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(InvestmentOpportunity, pk=opportunity_id)
    Vote.objects.filter(user=request.user, opportunity=opportunity).delete()
    return redirect('opportunities')


# -------------------- CREATE & EDIT OPPORTUNITY --------------------
@login_required
@staff_member_required
def create_opportunity(request):
    if request.method == 'POST':
        form = InvestmentOpportunityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Opportunity created.")
            return redirect('opportunities')
    else:
        form = InvestmentOpportunityForm()
    return render(request, 'core/create_opportunity.html', {'form': form})


@login_required
@staff_member_required
def edit_opportunity(request, pk):
    opportunity = get_object_or_404(InvestmentOpportunity, pk=pk)
    if request.method == 'POST':
        form = InvestmentOpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, "Opportunity updated successfully.")
            return redirect('opportunities')
    else:
        form = InvestmentOpportunityForm(instance=opportunity)
    return render(request, 'core/edit_opportunity.html', {'form': form, 'opportunity': opportunity})


# -------------------- LOGIN, LOGOUT, MISC --------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html')


def custom_logout(request):
    logout(request)
    return redirect('home')


def success_page(request):
    return render(request, 'core/success.html')


# -------------------- SAMPLE CHART DATA --------------------
def generate_sample_chart_data():
    return {
        "dates": ["Jan", "Feb", "Mar", "Apr", "May"],
        "values": [1000, 3000, 5000, 6500, 8000],
    }


from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
import tempfile

# Export Fund Summary PDF
def export_fund_summary_pdf(request):
    finances = MemberFinance.objects.select_related('user').all()
    template = get_template('core/fund_summary_pdf.html')
    html = template.render({'finances': finances})

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp:
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(temp.name)
        temp.seek(0)
        response = HttpResponse(temp.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="fund_summary.pdf"'
        return response



# Fund Edit Modal View
def edit_fund(request, pk):
    finance = get_object_or_404(MemberFinance, pk=pk)
    if request.method == 'POST':
        form = MemberFinanceForm(request.POST, instance=finance)
        if form.is_valid():
            form.save()
            return redirect('admin_summary')
    else:
        form = MemberFinanceForm(instance=finance)

    return render(request, 'core/edit_fund_modal.html', {'form': form, 'finance': finance})


@login_required
@staff_member_required
def download_single_user_report(request, user_id):
    user_finance = get_object_or_404(MemberFinance, user__id=user_id)
    template = get_template('core/single_user_report.html')
    html = template.render({'finance': user_finance})

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp:
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(temp.name)
        temp.seek(0)
        response = HttpResponse(temp.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{user_finance.user.username}_report.pdf"'
        return response


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from .models import InvestmentOpportunity

@user_passes_test(lambda u: u.is_superuser)
@login_required
def delete_opportunity(request, pk):
    opportunity = get_object_or_404(InvestmentOpportunity, pk=pk)
    opportunity.delete()
    return redirect('opportunity_list')  # Update with your actual list view name

def opportunity_list(request):
    opportunities = InvestmentOpportunity.objects.all()
    return render(request, 'core/opportunity_list.html', {'opportunities': opportunities})
