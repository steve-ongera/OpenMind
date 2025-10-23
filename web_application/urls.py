
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('chat/', views.chat_home_view, name='chat_home'),
    path('chat/new/', views.chat_session_view, name='chat_new'),
    path('chat/<uuid:session_id>/', views.chat_session_view, name='chat_session'),
    path('chat/<uuid:session_id>/send/', views.send_message_api, name='send_message'),
    path('chat/<uuid:session_id>/end/', views.end_chat_session, name='end_chat'),
    path('mood/', views.mood_tracker_view, name='mood_tracker'),
    path('resources/', views.resources_view, name='resources'),
    path('resources/<uuid:resource_id>/', views.resource_detail_view, name='resource_detail'),
    path('activities/', views.wellness_activities_view, name='activities'),
    path('forum/', views.forum_home_view, name='forum_home'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('crisis-support/', views.crisis_support_view, name='crisis_support'),
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('resources/', views.resources, name='resources'),
    path('community/', views.community, name='community'),
    path('find-therapist/', views.find_therapist, name='find_therapist'),
    path('crisis-support/', views.crisis_support, name='crisis_support'),
    
    # User Dashboard (requires authentication)
    path('quick-checkin/', views.quick_checkin, name='quick_checkin'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]

# Custom error handlers
handler404 = 'web_application.views.handler404'
handler500 = 'web_application.views.handler500'