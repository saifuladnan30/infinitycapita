from django.urls import path
from . import views
from .views import custom_logout, success_page
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('admin-summary/', views.admin_summary, name='admin_summary'),
    path('download-report/', views.download_report, name='download_report'),
    path('opportunities/', views.opportunities, name='opportunities'),
    path('vote/<int:opportunity_id>/<str:vote_choice>/', views.vote_opportunity, name='vote_opportunity'),
    path('create-opportunity/', views.create_opportunity, name='create_opportunity'),
    path('success/', success_page, name='success-page'),
    path('opportunity/<int:pk>/edit/', views.edit_opportunity, name='edit_opportunity'),
    path('vote/<int:opportunity_id>/<str:vote_choice>/', views.vote_opportunity, name='vote_opportunity'),
    path('unvote/<int:opportunity_id>/', views.unvote_opportunity, name='unvote_opportunity'),
    path('admin-summary/', views.admin_summary, name='admin_summary'),
    path('edit-fund/<int:pk>/', views.edit_fund, name='edit_fund'),
    path('export-fund-summary-pdf/', views.export_fund_summary_pdf, name='export_fund_summary_pdf'),
    path('download-report/<int:user_id>/', views.download_single_user_report, name='download_single_user_report'),
    path('opportunity/<int:pk>/delete/', views.delete_opportunity, name='delete_opportunity'),
    path('opportunities/', views.opportunity_list, name='opportunity_list'),


]
