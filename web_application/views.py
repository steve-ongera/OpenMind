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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import json

from .models import (
    User, UserProfile, ChatSession, ChatMessage,
    MoodEntry, CrisisAlert, ForumPost, ForumCategory,
    Resource, WellnessActivity, Notification,
    Achievement, UserStreak
)
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileUpdateForm,
    MoodEntryForm, ChatMessageForm
)


# ========================
# AUTHENTICATION VIEWS
# ========================

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                notification_preferences={
                    'email': True,
                    'push': True,
                    'mood_reminders': True
                }
            )
            
            # Create user streak
            UserStreak.objects.create(user=user)
            
            # Auto login after registration
            login(request, user)
            messages.success(request, f'Welcome to OpenMind, {user.first_name}! Your mental wellness journey starts here.')
            return redirect('onboarding')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Join OpenMind - Your Mental Wellness Companion'
    }
    return render(request, 'auth/register.html', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.account_suspended:
                    messages.error(request, 'Your account has been suspended. Please contact support.')
                    return redirect('login')
                
                login(request, user)
                user.last_active = timezone.now()
                user.save()
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect to next or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Sign In to OpenMind'
    }
    return render(request, 'auth/login.html', context)


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out. Take care of yourself!')
    return redirect('home')


# ========================
# ONBOARDING
# ========================

@login_required
def onboarding_view(request):
    """Onboarding flow for new users"""
    if request.method == 'POST':
        # Save onboarding data
        profile = request.user.profile
        profile.bio = request.POST.get('bio', '')
        
        # Save mental health preferences
        concerns = request.POST.getlist('concerns')
        goals = request.POST.getlist('goals')
        
        profile.accessibility_settings = {
            'concerns': concerns,
            'goals': goals,
            'preferred_communication': request.POST.get('communication', 'chat')
        }
        profile.save()
        
        messages.success(request, 'Profile setup complete! Let\'s start your wellness journey.')
        return redirect('dashboard')
    
    context = {
        'page_title': 'Welcome to OpenMind'
    }
    return render(request, 'auth/onboarding.html', context)


# ========================
# MAIN DASHBOARD
# ========================

@login_required
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    
    # Get user stats
    total_sessions = ChatSession.objects.filter(user=user).count()
    mood_entries = MoodEntry.objects.filter(user=user).count()
    
    # Recent mood entries (last 7 days)
    week_ago = timezone.now().date() - timedelta(days=7)
    recent_moods = MoodEntry.objects.filter(
        user=user,
        entry_date__gte=week_ago
    ).order_by('-entry_date')[:7]
    
    # Calculate average mood this week
    avg_mood = recent_moods.aggregate(Avg('mood_score'))['mood_score__avg'] or 0
    
    # Get streak info
    streak = UserStreak.objects.filter(user=user).first()
    
    # Recent notifications
    notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Recommended resources
    recommended_resources = Resource.objects.filter(
        is_published=True,
        is_featured=True
    ).order_by('-view_count')[:3]
    
    # Active crisis alerts
    active_crisis = CrisisAlert.objects.filter(
        user=user,
        status__in=['detected', 'acknowledged']
    ).exists()
    
    context = {
        'total_sessions': total_sessions,
        'mood_entries_count': mood_entries,
        'recent_moods': recent_moods,
        'avg_mood': round(avg_mood, 1),
        'streak': streak,
        'notifications': notifications,
        'recommended_resources': recommended_resources,
        'active_crisis': active_crisis,
        'page_title': 'Dashboard'
    }
    return render(request, 'dashboard/home.html', context)


# ========================
# CHAT INTERFACE (MAIN FEATURE)
# ========================

@login_required
def chat_home_view(request):
    """Chat home - shows recent sessions and start new chat"""
    user = request.user
    
    # Get recent chat sessions
    recent_sessions = ChatSession.objects.filter(
        user=user
    ).order_by('-started_at')[:10]
    
    # Get active session if any
    active_session = ChatSession.objects.filter(
        user=user,
        status='active'
    ).first()
    
    context = {
        'recent_sessions': recent_sessions,
        'active_session': active_session,
        'page_title': 'Talk to OpenMind AI'
    }
    return render(request, 'chat/home.html', context)


@login_required
def chat_session_view(request, session_id=None):
    """Main chat interface - ChatGPT-like experience"""
    user = request.user
    
    if session_id:
        # Load existing session
        session = get_object_or_404(ChatSession, id=session_id, user=user)
        messages_list = ChatMessage.objects.filter(session=session).order_by('created_at')
    else:
        # Create new session
        session = ChatSession.objects.create(
            user=user,
            session_title='New Conversation',
            status='active',
            ai_model_version='OpenMind-AI-v1',
            therapy_framework='CBT'
        )
        messages_list = []
        
        # Create welcome message
        welcome_msg = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message_text="Hello! I'm OpenMind AI, your mental wellness companion. I'm here to listen, support, and help you navigate your feelings. How are you feeling today?",
            sentiment_score=0.8
        )
        messages_list = [welcome_msg]
    
    # Check for crisis indicators
    crisis_detected = session.crisis_detected
    
    context = {
        'session': session,
        'messages': messages_list,
        'crisis_detected': crisis_detected,
        'page_title': session.session_title or 'Chat with OpenMind AI'
    }
    return render(request, 'chat/session.html', context)


@login_required
@require_http_methods(["POST"])
def send_message_api(request, session_id):
    """API endpoint to send and receive messages"""
    try:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Create user message
        user_msg = ChatMessage.objects.create(
            session=session,
            sender='user',
            message_text=user_message
        )
        
        # Analyze message for crisis keywords (simplified)
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hopeless', 'want to die']
        contains_crisis = any(keyword in user_message.lower() for keyword in crisis_keywords)
        
        if contains_crisis:
            user_msg.contains_crisis_keywords = True
            user_msg.requires_intervention = True
            user_msg.save()
            
            # Update session
            session.crisis_detected = True
            session.crisis_severity = 8
            session.save()
            
            # Create crisis alert
            CrisisAlert.objects.create(
                user=request.user,
                chat_session=session,
                severity='high',
                crisis_type='suicidal_ideation',
                triggering_content=user_message,
                ai_confidence_score=0.85,
                keywords_matched=crisis_keywords
            )
        
        # Generate AI response (simplified - in production, use actual AI API)
        bot_response_text = generate_ai_response(user_message, contains_crisis)
        
        # Create bot message
        bot_msg = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message_text=bot_response_text,
            sentiment_score=0.7
        )
        
        # Update session
        session.total_messages += 2
        session.save()
        
        response_data = {
            'success': True,
            'user_message': {
                'id': str(user_msg.id),
                'text': user_msg.message_text,
                'timestamp': user_msg.created_at.isoformat()
            },
            'bot_message': {
                'id': str(bot_msg.id),
                'text': bot_msg.message_text,
                'timestamp': bot_msg.created_at.isoformat()
            },
            'crisis_detected': contains_crisis
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def generate_ai_response(user_message, is_crisis):
    """Generate AI response (simplified version)"""
    if is_crisis:
        return """I'm really concerned about what you're sharing with me. Your safety is the most important thing right now. 

**Please reach out for immediate help:**
- National Crisis Hotline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911

You don't have to face this alone. Would you like me to help you connect with a professional counselor right now?"""
    
    # Simple response generation based on keywords
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'nervous']):
        return """I hear that you're feeling anxious. That's a very common experience, and it's brave of you to talk about it. 

Let's try a quick grounding exercise together:
1. Name 5 things you can see
2. 4 things you can touch
3. 3 things you can hear
4. 2 things you can smell
5. 1 thing you can taste

Would you like to try this, or would you prefer to talk more about what's making you feel anxious?"""
    
    elif any(word in message_lower for word in ['sad', 'depressed', 'down', 'lonely']):
        return """Thank you for sharing how you're feeling. It takes courage to acknowledge when we're struggling. Feeling sad or down is a valid emotional experience.

Can you tell me a bit more about what's been going on? Sometimes talking through our feelings can help us understand them better. I'm here to listen without judgment."""
    
    elif any(word in message_lower for word in ['stressed', 'stress', 'overwhelmed', 'pressure']):
        return """It sounds like you're dealing with a lot of stress right now. That can be really exhausting, both mentally and physically.

Let's break this down together. What's the main source of stress for you right now? Sometimes identifying the specific stressors can help us develop strategies to manage them better.

Have you tried any stress-relief techniques that have worked for you in the past?"""
    
    elif any(word in message_lower for word in ['thank', 'better', 'helped', 'good']):
        return """I'm so glad I could help! Remember, taking care of your mental health is an ongoing journey, and it's wonderful that you're being proactive about it.

Feel free to come back anytime you need support. Is there anything else you'd like to talk about today?"""
    
    else:
        return """I appreciate you sharing that with me. Your feelings and experiences are valid and important.

Could you tell me a bit more about what's on your mind? I'm here to listen and support you in whatever way I can. Whether you're dealing with stress, anxiety, or just need someone to talk to, this is a safe space for you."""


@login_required
def end_chat_session(request, session_id):
    """End a chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.status = 'ended'
    session.ended_at = timezone.now()
    session.save()
    
    messages.success(request, 'Chat session ended. Your conversation has been saved.')
    return redirect('chat_home')


# ========================
# MOOD TRACKING
# ========================

@login_required
def mood_tracker_view(request):
    """Mood tracking interface"""
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood_entry = form.save(commit=False)
            mood_entry.user = request.user
            mood_entry.entry_date = timezone.now().date()
            mood_entry.save()
            
            # Update streak
            streak = UserStreak.objects.get_or_create(user=request.user)[0]
            if streak.last_mood_entry == timezone.now().date() - timedelta(days=1):
                streak.current_mood_streak += 1
                if streak.current_mood_streak > streak.longest_mood_streak:
                    streak.longest_mood_streak = streak.current_mood_streak
            else:
                streak.current_mood_streak = 1
            
            streak.last_mood_entry = timezone.now().date()
            streak.total_points += 10
            streak.save()
            
            messages.success(request, f'Mood logged! You earned 10 points. Current streak: {streak.current_mood_streak} days!')
            return redirect('mood_tracker')
    else:
        form = MoodEntryForm()
    
    # Get mood history
    mood_history = MoodEntry.objects.filter(
        user=request.user
    ).order_by('-entry_date')[:30]
    
    context = {
        'form': form,
        'mood_history': mood_history,
        'page_title': 'Mood Tracker'
    }
    return render(request, 'mood/tracker.html', context)


# ========================
# RESOURCES & ACTIVITIES
# ========================

@login_required
def resources_view(request):
    """Browse mental health resources"""
    resource_type = request.GET.get('type', 'all')
    
    resources = Resource.objects.filter(is_published=True)
    
    if resource_type != 'all':
        resources = resources.filter(resource_type=resource_type)
    
    resources = resources.order_by('-is_featured', '-created_at')
    
    context = {
        'resources': resources,
        'resource_type': resource_type,
        'page_title': 'Mental Health Resources'
    }
    return render(request, 'resources/list.html', context)


@login_required
def resource_detail_view(request, resource_id):
    """View a specific resource"""
    resource = get_object_or_404(Resource, id=resource_id, is_published=True)
    
    # Increment view count
    resource.view_count += 1
    resource.save()
    
    context = {
        'resource': resource,
        'page_title': resource.title
    }
    return render(request, 'resources/detail.html', context)


@login_required
def wellness_activities_view(request):
    """Browse wellness activities"""
    activities = WellnessActivity.objects.filter(is_active=True).order_by('activity_type')
    
    context = {
        'activities': activities,
        'page_title': 'Wellness Activities'
    }
    return render(request, 'activities/list.html', context)


# ========================
# COMMUNITY FORUM
# ========================

@login_required
def forum_home_view(request):
    """Community forum home"""
    categories = ForumCategory.objects.filter(is_active=True)
    
    recent_posts = ForumPost.objects.filter(
        is_published=True
    ).order_by('-created_at')[:10]
    
    context = {
        'categories': categories,
        'recent_posts': recent_posts,
        'page_title': 'Community Forum'
    }
    return render(request, 'forum/home.html', context)


# ========================
# PROFILE & SETTINGS
# ========================

@login_required
def profile_view(request):
    """User profile view"""
    profile = request.user.profile
    streak = UserStreak.objects.get_or_create(user=request.user)[0]
    
    # Get achievements
    user_achievements = request.user.achievements.all()
    
    # Get stats
    stats = {
        'total_sessions': ChatSession.objects.filter(user=request.user).count(),
        'mood_entries': MoodEntry.objects.filter(user=request.user).count(),
        'forum_posts': ForumPost.objects.filter(author=request.user).count(),
        'total_points': streak.total_points
    }
    
    context = {
        'profile': profile,
        'streak': streak,
        'achievements': user_achievements,
        'stats': stats,
        'page_title': 'My Profile'
    }
    return render(request, 'profile/view.html', context)


@login_required
def settings_view(request):
    """User settings"""
    if request.method == 'POST':
        # Update settings logic here
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    context = {
        'page_title': 'Settings'
    }
    return render(request, 'profile/settings.html', context)


# ========================
# CRISIS SUPPORT
# ========================

@login_required
def crisis_support_view(request):
    """Crisis support resources"""
    user_country = request.user.country
    
    crisis_resources = CrisisAlert.objects.filter(
        country=user_country,
        is_active=True
    )
    
    context = {
        'crisis_resources': crisis_resources,
        'page_title': 'Crisis Support'
    }
    return render(request, 'crisis/support.html', context)


# ========================
# PUBLIC PAGES
# ========================




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