
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    
    # Resources & Community
    path('resources/', views.resources, name='resources'),
    path('community/', views.community, name='community'),
    
    # Therapist
    path('find-therapist/', views.find_therapist, name='find_therapist'),
    
    # Crisis Support
    path('crisis-support/', views.crisis_support, name='crisis_support'),
    
    # User Dashboard (requires authentication)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Forms
    path('quick-checkin/', views.quick_checkin, name='quick_checkin'),
    
    # Legal pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]

# Custom error handlers
handler404 = 'web_application.views.handler404'
handler500 = 'web_application.views.handler500'