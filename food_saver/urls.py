from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_food, name='upload_food'),
    path('claim/<int:donation_id>/', views.claim_donation, name='claim_donation'),
    path('volunteer/accept/<int:donation_id>/', views.volunteer_accept_task, name='volunteer_accept_task'),
    path('volunteer/pickup/<int:pickup_id>/', views.volunteer_confirm_pickup, name='volunteer_confirm_pickup'),
    path('volunteer/delivery/<int:pickup_id>/', views.volunteer_confirm_delivery, name='volunteer_confirm_delivery'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/toggle-fraud/<int:user_id>/', views.toggle_fraud, name='toggle_fraud'),
    path('donation/<int:donation_id>/', views.donation_detail, name='donation_detail'),
]
