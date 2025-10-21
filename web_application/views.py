from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    User, ChatSession, MoodEntry, CrisisAlert,
    ForumPost, ForumCategory, Resource, WellnessActivity,
    TherapistProfile, CounselingAppointment, PlatformAnalytics
)


def home(request):
    """
    Homepage view with platform statistics and featured content
    """
    # Get platform statistics
    total_users = User.objects.filter(is_active=True).count()
    total_chat_sessions = ChatSession.objects.count()
    total_therapists = TherapistProfile.objects.filter(is_verified=True).count()
    
    # Get featured resources
    featured_resources = Resource.objects.filter(
        is_featured=True, 
        is_published=True
    ).order_by('-created_at')[:3]
    
    # Get recent forum posts
    recent_forum_posts = ForumPost.objects.filter(
        is_published=True
    ).select_related('author', 'category').order_by('-created_at')[:5]
    
    # Get popular wellness activities
    popular_activities = WellnessActivity.objects.filter(
        is_active=True
    ).annotate(
        completion_count=Count('completion_logs')
    ).order_by('-completion_count')[:4]
    
    context = {
        'total_users': total_users,
        'total_chat_sessions': total_chat_sessions,
        'total_therapists': total_therapists,
        'featured_resources': featured_resources,
        'recent_forum_posts': recent_forum_posts,
        'popular_activities': popular_activities,
    }
    
    return render(request, 'index.html', context)


def about(request):
    """About page view"""
    # Get team statistics
    total_therapists = TherapistProfile.objects.filter(is_verified=True).count()
    total_sessions = CounselingAppointment.objects.filter(status='completed').count()
    
    # Get average ratings
    avg_platform_rating = TherapistProfile.objects.aggregate(
        avg_rating=Avg('average_rating')
    )['avg_rating'] or 0
    
    context = {
        'total_therapists': total_therapists,
        'total_sessions': total_sessions,
        'avg_platform_rating': round(avg_platform_rating, 1),
    }
    
    return render(request, 'about.html', context)


def services(request):
    """Services page view"""
    services_list = [
        {
            'name': 'AI Therapy Chatbot',
            'icon': 'icon-comment-o',
            'description': '24/7 conversational support using advanced NLP and therapeutic frameworks.',
            'features': ['CBT & DBT frameworks', 'Crisis detection', 'Multilingual support', 'Personalized responses']
        },
        {
            'name': 'Mood Tracking',
            'icon': 'icon-heart-o',
            'description': 'Track your emotional well-being and discover patterns.',
            'features': ['Daily mood logging', 'AI pattern analysis', 'Trigger identification', 'Progress visualization']
        },
        {
            'name': 'Professional Counseling',
            'icon': 'icon-user-md',
            'description': 'Connect with verified therapists for personalized sessions.',
            'features': ['Video/Audio/Chat sessions', 'Verified professionals', 'Flexible scheduling', 'Secure platform']
        },
        {
            'name': 'Community Forum',
            'icon': 'icon-users',
            'description': 'Safe space for peer support and shared experiences.',
            'features': ['Moderated discussions', 'Anonymous posting', 'Topic categories', 'Expert insights']
        },
        {
            'name': 'Wellness Activities',
            'icon': 'icon-leaf',
            'description': 'Guided activities for mental and emotional wellness.',
            'features': ['Meditation guides', 'Breathing exercises', 'Journaling prompts', 'Mindfulness practices']
        },
        {
            'name': 'Resource Library',
            'icon': 'icon-book',
            'description': 'Curated mental health content and educational materials.',
            'features': ['Articles & videos', 'Worksheets', 'Expert advice', 'Self-help tools']
        },
    ]
    
    context = {
        'services': services_list,
    }
    
    return render(request, 'services.html', context)


def resources(request):
    """Resources library view"""
    # Get filter parameters
    resource_type = request.GET.get('type', '')
    topic = request.GET.get('topic', '')
    search_query = request.GET.get('q', '')
    
    # Base queryset
    resources_list = Resource.objects.filter(is_published=True)
    
    # Apply filters
    if resource_type:
        resources_list = resources_list.filter(resource_type=resource_type)
    
    if topic:
        resources_list = resources_list.filter(mental_health_topics__contains=[topic])
    
    if search_query:
        resources_list = resources_list.filter(
            title__icontains=search_query
        ) | resources_list.filter(
            description__icontains=search_query
        )
    
    # Order by featured first, then by views
    resources_list = resources_list.order_by('-is_featured', '-view_count')
    
    # Get unique resource types and topics for filters
    resource_types = Resource.RESOURCE_TYPES
    
    context = {
        'resources': resources_list,
        'resource_types': resource_types,
        'selected_type': resource_type,
        'selected_topic': topic,
        'search_query': search_query,
    }
    
    return render(request, 'resources.html', context)


def community(request):
    """Community forum view"""
    # Get forum categories with post counts
    categories = ForumCategory.objects.filter(
        is_active=True
    ).annotate(
        post_count=Count('posts')
    ).order_by('display_order')
    
    # Get recent posts
    recent_posts = ForumPost.objects.filter(
        is_published=True
    ).select_related('author', 'category').order_by('-created_at')[:10]
    
    # Get popular posts (by likes and replies)
    popular_posts = ForumPost.objects.filter(
        is_published=True
    ).order_by('-like_count', '-reply_count')[:5]
    
    context = {
        'categories': categories,
        'recent_posts': recent_posts,
        'popular_posts': popular_posts,
    }
    
    return render(request, 'community.html', context)


def find_therapist(request):
    """Find therapist view"""
    # Get filter parameters
    specialization = request.GET.get('specialization', '')
    language = request.GET.get('language', '')
    min_experience = request.GET.get('experience', 0)
    
    # Base queryset - only verified and available therapists
    therapists = TherapistProfile.objects.filter(
        is_verified=True,
        available_for_sessions=True
    ).select_related('user')
    
    # Apply filters
    if specialization:
        therapists = therapists.filter(specializations__contains=[specialization])
    
    if language:
        therapists = therapists.filter(languages_spoken__contains=[language])
    
    if min_experience:
        therapists = therapists.filter(years_of_experience__gte=int(min_experience))
    
    # Order by rating and experience
    therapists = therapists.order_by('-average_rating', '-years_of_experience')
    
    context = {
        'therapists': therapists,
        'selected_specialization': specialization,
        'selected_language': language,
        'min_experience': min_experience,
    }
    
    return render(request, 'find_therapist.html', context)


def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, just show success message
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'contact.html')


def crisis_support(request):
    """Crisis support and resources page"""
    # Get crisis resources by country (you can make this dynamic based on user location)
    user_country = getattr(request.user, 'country', 'US') if request.user.is_authenticated else 'US'
    
    from .models import CrisisResource
    crisis_resources = CrisisResource.objects.filter(
        country=user_country,
        is_active=True
    ).order_by('-available_24_7', 'name')
    
    # If no resources for user's country, show international resources
    if not crisis_resources.exists():
        crisis_resources = CrisisResource.objects.filter(
            is_active=True
        ).order_by('-available_24_7', 'name')[:10]
    
    context = {
        'crisis_resources': crisis_resources,
        'user_country': user_country,
    }
    
    return render(request, 'crisis_support.html', context)


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user
    
    # Get user's recent activity
    recent_mood_entries = MoodEntry.objects.filter(
        user=user
    ).order_by('-entry_date')[:7]
    
    recent_chat_sessions = ChatSession.objects.filter(
        user=user
    ).order_by('-started_at')[:5]
    
    upcoming_appointments = CounselingAppointment.objects.filter(
        client=user,
        scheduled_date__gte=timezone.now().date(),
        status__in=['scheduled', 'confirmed']
    ).order_by('scheduled_date', 'scheduled_time')[:5]
    
    # Get user's streak
    from .models import UserStreak
    try:
        streak = UserStreak.objects.get(user=user)
    except UserStreak.DoesNotExist:
        streak = None
    
    # Calculate mood trend
    if recent_mood_entries:
        avg_mood = sum([entry.mood_score for entry in recent_mood_entries]) / len(recent_mood_entries)
    else:
        avg_mood = 0
    
    # Get recommendations
    from .models import AIRecommendation
    recommendations = AIRecommendation.objects.filter(
        user=user,
        viewed=False,
        dismissed=False
    ).order_by('-priority', '-created_at')[:5]
    
    context = {
        'recent_mood_entries': recent_mood_entries,
        'recent_chat_sessions': recent_chat_sessions,
        'upcoming_appointments': upcoming_appointments,
        'streak': streak,
        'avg_mood': round(avg_mood, 1),
        'recommendations': recommendations,
    }
    
    return render(request, 'dashboard.html', context)


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'privacy_policy.html')


def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'terms_of_service.html')


def quick_checkin(request):
    """Handle quick check-in form from homepage"""
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        concern = request.POST.get('concern')
        message = request.POST.get('message')
        
        # Here you would typically:
        # 1. Create a user account or lead
        # 2. Send welcome email
        # 3. Redirect to appropriate service based on concern
        
        messages.success(
            request, 
            f'Thank you {fname}! We\'ve received your information. Check your email for next steps.'
        )
        
        # Redirect based on concern
        if concern == 'crisis':
            return redirect('crisis_support')
        else:
            return redirect('home')
    
    return redirect('home')


# Error handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)