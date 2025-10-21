from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid


# ========================
# USER MANAGEMENT
# ========================

class User(AbstractUser):
    """Extended user model with mental health platform specific fields"""
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('child', 'Child/Teen'),
        ('adult', 'Adult'),
        ('therapist', 'Professional Therapist'),
        ('moderator', 'Community Moderator'),
        ('admin', 'Platform Admin'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-Binary'),
        ('prefer_not_to_say', 'Prefer Not to Say'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Privacy settings
    is_anonymous = models.BooleanField(default=False)
    data_sharing_consent = models.BooleanField(default=False)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    account_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['user_type', 'country']),
            models.Index(fields=['created_at']),
        ]


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Student specific
    university = models.CharField(max_length=200, blank=True)
    field_of_study = models.CharField(max_length=200, blank=True)
    academic_year = models.CharField(max_length=50, blank=True)
    
    # Mental health background
    has_previous_therapy = models.BooleanField(default=False)
    current_medications = models.TextField(blank=True)
    diagnosed_conditions = models.TextField(blank=True)
    
    # Preferences
    notification_preferences = models.JSONField(default=dict)
    accessibility_settings = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'


class EmergencyContact(models.Model):
    """Emergency contacts for crisis situations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)
    can_be_contacted_during_crisis = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emergency_contacts'
        ordering = ['-is_primary', 'name']


# ========================
# THERAPIST/PROFESSIONAL
# ========================

class TherapistProfile(models.Model):
    """Professional therapist credentials and information"""
    SPECIALIZATION_CHOICES = [
        ('clinical_psychology', 'Clinical Psychology'),
        ('counseling', 'Counseling'),
        ('psychiatry', 'Psychiatry'),
        ('cbt', 'Cognitive Behavioral Therapy'),
        ('child_psychology', 'Child Psychology'),
        ('trauma', 'Trauma Therapy'),
        ('addiction', 'Addiction Counseling'),
        ('family_therapy', 'Family Therapy'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile')
    license_number = models.CharField(max_length=100, unique=True)
    specializations = models.JSONField(default=list)
    years_of_experience = models.IntegerField(validators=[MinValueValidator(0)])
    education = models.TextField()
    certifications = models.TextField()
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(default=list)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_therapists')
    
    # Practice details
    practice_name = models.CharField(max_length=200, blank=True)
    practice_address = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accepts_insurance = models.BooleanField(default=False)
    languages_spoken = models.JSONField(default=list)
    
    # Availability
    available_for_sessions = models.BooleanField(default=True)
    max_clients = models.IntegerField(default=20)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sessions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'therapist_profiles'


class TherapistAvailability(models.Model):
    """Weekly availability schedule for therapists"""
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'therapist_availability'
        unique_together = ['therapist', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']


# ========================
# AI CHATBOT / THERAPY BOT
# ========================

class ChatSession(models.Model):
    """Individual chat sessions with TherapyBot"""
    SESSION_STATUS = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('escalated', 'Escalated to Human'),
        ('crisis_detected', 'Crisis Detected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_title = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    
    # AI model tracking
    ai_model_version = models.CharField(max_length=50)
    therapy_framework = models.CharField(max_length=50, default='CBT')
    
    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_messages = models.IntegerField(default=0)
    
    # Crisis tracking
    crisis_detected = models.BooleanField(default=False)
    crisis_severity = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    crisis_handled = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['crisis_detected', 'crisis_handled']),
        ]


class ChatMessage(models.Model):
    """Individual messages in chat sessions"""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'AI Bot'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_text = models.TextField()
    
    # AI analysis
    sentiment_score = models.FloatField(null=True, blank=True)
    emotion_detected = models.JSONField(default=dict)
    intent_classification = models.CharField(max_length=100, blank=True)
    keywords_extracted = models.JSONField(default=list)
    
    # Crisis flags
    contains_crisis_keywords = models.BooleanField(default=False)
    suicide_risk_score = models.FloatField(null=True, blank=True)
    requires_intervention = models.BooleanField(default=False)
    
    # Message metadata
    is_flagged = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['requires_intervention']),
        ]


class BotResponse(models.Model):
    """Tracks bot response patterns for improvement"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='bot_responses')
    response_template = models.CharField(max_length=100, blank=True)
    confidence_score = models.FloatField()
    
    # User feedback
    user_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    was_helpful = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bot_responses'


# ========================
# MOOD TRACKING
# ========================

class MoodEntry(models.Model):
    """Daily mood logs by users"""
    MOOD_CHOICES = [
        ('very_bad', 'Very Bad'),
        ('bad', 'Bad'),
        ('neutral', 'Neutral'),
        ('good', 'Good'),
        ('very_good', 'Very Good'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    
    # Mood data
    mood_level = models.CharField(max_length=20, choices=MOOD_CHOICES)
    mood_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    emotions = models.JSONField(default=list)
    
    # Context
    energy_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    sleep_quality = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    sleep_hours = models.FloatField(null=True, blank=True)
    
    # Activities and triggers
    activities = models.JSONField(default=list)
    triggers = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Location and time
    location = models.CharField(max_length=100, blank=True)
    weather = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    entry_date = models.DateField()
    
    class Meta:
        db_table = 'mood_entries'
        ordering = ['-entry_date', '-created_at']
        unique_together = ['user', 'entry_date']
        indexes = [
            models.Index(fields=['user', '-entry_date']),
        ]
        verbose_name_plural = 'Mood entries'


class MoodPattern(models.Model):
    """AI-analyzed mood patterns over time"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_patterns')
    
    # Time period
    start_date = models.DateField()
    end_date = models.DateField()
    period_type = models.CharField(max_length=20)
    
    # Pattern analysis
    average_mood_score = models.FloatField()
    mood_variance = models.FloatField()
    trend_direction = models.CharField(max_length=20)
    
    # Insights
    dominant_emotions = models.JSONField(default=list)
    common_triggers = models.JSONField(default=list)
    positive_activities = models.JSONField(default=list)
    
    # AI recommendations
    recommendations = models.TextField()
    concern_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mood_patterns'
        ordering = ['-end_date']


# ========================
# CRISIS MANAGEMENT
# ========================

class CrisisAlert(models.Model):
    """Crisis detection and intervention tracking"""
    SEVERITY_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical - Immediate Intervention'),
    ]
    
    STATUS_CHOICES = [
        ('detected', 'Detected'),
        ('acknowledged', 'Acknowledged'),
        ('contacted', 'Emergency Contact Made'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated to Professional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crisis_alerts')
    
    # Detection source
    chat_session = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, blank=True)
    mood_entry = models.ForeignKey(MoodEntry, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Crisis details
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected')
    crisis_type = models.CharField(max_length=100)
    
    # Detection data
    triggering_content = models.TextField()
    ai_confidence_score = models.FloatField()
    keywords_matched = models.JSONField(default=list)
    
    # Response
    intervention_taken = models.TextField(blank=True)
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crisis_responses')
    emergency_services_contacted = models.BooleanField(default=False)
    emergency_contact_notified = models.BooleanField(default=False)
    
    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'crisis_alerts'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['user', '-detected_at']),
        ]


class CrisisResource(models.Model):
    """Crisis hotlines and resources by region"""
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    resource_type = models.CharField(max_length=50)
    
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    chat_url = models.URLField(blank=True)
    address = models.TextField(blank=True)
    
    available_24_7 = models.BooleanField(default=False)
    languages_supported = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crisis_resources'
        indexes = [
            models.Index(fields=['country', 'is_active']),
        ]


# ========================
# COMMUNITY FORUM
# ========================

class ForumCategory(models.Model):
    """Forum topic categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_categories'
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Forum categories'


class ForumPost(models.Model):
    """Forum discussion posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    
    title = models.CharField(max_length=300)
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    
    # Engagement
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    
    # Moderation
    is_published = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    moderation_status = models.CharField(max_length=20, default='approved')
    
    # AI moderation
    toxicity_score = models.FloatField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    ai_flagged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_posts'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]


class ForumReply(models.Model):
    """Replies to forum posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='nested_replies')
    
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    
    # Engagement
    like_count = models.IntegerField(default=0)
    
    # Moderation
    is_published = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    toxicity_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_replies'
        ordering = ['created_at']
        verbose_name_plural = 'Forum replies'


class ForumLike(models.Model):
    """Track likes on posts and replies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    reply = models.ForeignKey(ForumReply, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_likes'
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like'),
            models.UniqueConstraint(fields=['user', 'reply'], name='unique_user_reply_like'),
        ]


class ForumReport(models.Model):
    """User reports for inappropriate content"""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('self_harm', 'Self-Harm Content'),
        ('misinformation', 'Misinformation'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reply = models.ForeignKey(ForumReply, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField()
    
    # Moderation
    status = models.CharField(max_length=20, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    action_taken = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'forum_reports'
        ordering = ['-created_at']


# ========================
# COUNSELING SESSIONS
# ========================

class CounselingAppointment(models.Model):
    """Professional therapy sessions"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    SESSION_TYPE = [
        ('video', 'Video Call'),
        ('audio', 'Audio Call'),
        ('chat', 'Text Chat'),
        ('in_person', 'In Person'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='counseling_appointments')
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment details
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Session info
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    notes_for_therapist = models.TextField(blank=True)
    
    # Payment
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Post-session
    attended = models.BooleanField(null=True, blank=True)
    session_notes = models.TextField(blank=True)
    next_session_recommended = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'counseling_appointments'
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['client', '-scheduled_date']),
            models.Index(fields=['therapist', '-scheduled_date']),
            models.Index(fields=['status', 'scheduled_date']),
        ]


class SessionNote(models.Model):
    """Private notes from therapy sessions (HIPAA compliant)"""
    appointment = models.OneToOneField(CounselingAppointment, on_delete=models.CASCADE, related_name='private_notes')
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name='session_notes')
    
    # Clinical notes
    presenting_issue = models.TextField()
    observations = models.TextField()
    interventions_used = models.TextField()
    client_response = models.TextField()
    homework_assigned = models.TextField(blank=True)
    
    # Assessment
    risk_assessment = models.TextField()
    progress_notes = models.TextField()
    treatment_plan_updates = models.TextField(blank=True)
    
    # Next steps
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    referrals_made = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'session_notes'


class TherapistReview(models.Model):
    """Client reviews and ratings for therapists"""
    appointment = models.OneToOneField(CounselingAppointment, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    
    # Rating dimensions
    professionalism = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    effectiveness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    empathy = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    would_recommend = models.BooleanField()
    is_anonymous = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'therapist_reviews'
        ordering = ['-created_at']


# ========================
# RESOURCES & RECOMMENDATIONS
# ========================

class Resource(models.Model):
    """Mental health resources and content"""
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio/Podcast'),
        ('exercise', 'Exercise'),
        ('meditation', 'Meditation'),
        ('journal_prompt', 'Journal Prompt'),
        ('worksheet', 'Worksheet'),
        ('infographic', 'Infographic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField()
    
    # Content
    content = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='resources/', null=True, blank=True)
    
    # Metadata
    author = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    difficulty_level = models.CharField(max_length=20, blank=True)
    
    # Categorization
    tags = models.JSONField(default=list)
    target_audience = models.JSONField(default=list)
    mental_health_topics = models.JSONField(default=list)
    
    # Multilingual
    language = models.CharField(max_length=10, default='en')
    translations_available = models.JSONField(default=list)
    
    # Engagement
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource_type', '-created_at']),
            models.Index(fields=['is_featured', '-view_count']),
        ]


class UserResourceInteraction(models.Model):
    """Track user interactions with resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_interactions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='interactions')
    
    # Interaction type
    viewed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    
    # Feedback
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    was_helpful = models.BooleanField(null=True, blank=True)
    
    # Progress tracking
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    time_spent_minutes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_resource_interactions'
        unique_together = ['user', 'resource']


class AIRecommendation(models.Model):
    """AI-generated personalized recommendations"""
    RECOMMENDATION_TYPES = [
        ('resource', 'Resource'),
        ('activity', 'Activity'),
        ('therapist', 'Therapist'),
        ('crisis_resource', 'Crisis Resource'),
        ('coping_strategy', 'Coping Strategy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    
    # Recommendation content
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    # Links to specific items
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, null=True, blank=True)
    
    # AI reasoning
    reason = models.TextField()
    confidence_score = models.FloatField()
    based_on_data = models.JSONField(default=dict)
    
    # User interaction
    viewed = models.BooleanField(default=False)
    acted_upon = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    feedback_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    priority = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_recommendations'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['viewed', 'dismissed']),
        ]


# ========================
# ACTIVITIES & WELLNESS
# ========================

class WellnessActivity(models.Model):
    """Wellness activities and exercises"""
    ACTIVITY_TYPES = [
        ('breathing', 'Breathing Exercise'),
        ('meditation', 'Meditation'),
        ('journaling', 'Journaling'),
        ('physical', 'Physical Exercise'),
        ('mindfulness', 'Mindfulness'),
        ('grounding', 'Grounding Technique'),
        ('gratitude', 'Gratitude Practice'),
        ('creative', 'Creative Expression'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    instructions = models.TextField()
    
    duration_minutes = models.IntegerField()
    difficulty = models.CharField(max_length=20)
    
    # Media
    audio_guide_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='activities/', null=True, blank=True)
    
    # Benefits
    benefits = models.JSONField(default=list)
    best_for = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wellness_activities'
        verbose_name_plural = 'Wellness activities'


class UserActivityLog(models.Model):
    """Track user completion of wellness activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity = models.ForeignKey(WellnessActivity, on_delete=models.CASCADE, related_name='completion_logs')
    
    completed = models.BooleanField(default=False)
    duration_minutes = models.IntegerField()
    
    # Pre/post mood
    mood_before = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    mood_after = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    notes = models.TextField(blank=True)
    was_helpful = models.BooleanField(null=True, blank=True)
    
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        ordering = ['-completed_at']


class JournalEntry(models.Model):
    """User journaling entries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    
    # Prompts
    prompt_used = models.CharField(max_length=500, blank=True)
    
    # AI analysis
    sentiment_score = models.FloatField(null=True, blank=True)
    emotions_detected = models.JSONField(default=dict)
    themes = models.JSONField(default=list)
    
    # Privacy
    is_private = models.BooleanField(default=True)
    
    # Mood at time of writing
    mood_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'journal_entries'
        ordering = ['-created_at']
        verbose_name_plural = 'Journal entries'


# ========================
# NOTIFICATIONS
# ========================

class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment Reminder'),
        ('mood_check', 'Mood Check-in'),
        ('recommendation', 'New Recommendation'),
        ('message', 'New Message'),
        ('forum', 'Forum Activity'),
        ('crisis', 'Crisis Alert'),
        ('achievement', 'Achievement Unlocked'),
        ('system', 'System Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Links
    link_url = models.CharField(max_length=500, blank=True)
    action_button_text = models.CharField(max_length=100, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    priority = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]


# ========================
# GAMIFICATION
# ========================

class Achievement(models.Model):
    """Achievement badges and milestones"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    
    # Requirements
    requirement_type = models.CharField(max_length=50)
    requirement_count = models.IntegerField()
    
    # Points
    points = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievements'


class UserAchievement(models.Model):
    """Track user achievements"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earned_by')
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = ['user', 'achievement']


class UserStreak(models.Model):
    """Track user engagement streaks"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    
    # Streaks
    current_mood_streak = models.IntegerField(default=0)
    longest_mood_streak = models.IntegerField(default=0)
    current_activity_streak = models.IntegerField(default=0)
    longest_activity_streak = models.IntegerField(default=0)
    
    # Last activity dates
    last_mood_entry = models.DateField(null=True, blank=True)
    last_activity = models.DateField(null=True, blank=True)
    
    # Points
    total_points = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_streaks'


# ========================
# ANALYTICS & REPORTING
# ========================

class PlatformAnalytics(models.Model):
    """Aggregate platform statistics for research and reporting"""
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    
    # Engagement
    total_chat_sessions = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    total_mood_entries = models.IntegerField(default=0)
    total_forum_posts = models.IntegerField(default=0)
    
    # Crisis
    crisis_alerts = models.IntegerField(default=0)
    crisis_interventions = models.IntegerField(default=0)
    
    # Professional services
    total_appointments = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    
    # Geographic data (anonymized)
    users_by_country = models.JSONField(default=dict)
    users_by_age_group = models.JSONField(default=dict)
    
    # Sentiment trends
    average_mood_score = models.FloatField(null=True, blank=True)
    average_sentiment = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'platform_analytics'
        ordering = ['-date']
        verbose_name_plural = 'Platform analytics'


class RegionalMentalHealthTrend(models.Model):
    """Regional mental health trends for research (anonymized)"""
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    year = models.IntegerField()
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    # Aggregate data
    total_users = models.IntegerField()
    common_concerns = models.JSONField(default=list)
    average_mood_score = models.FloatField()
    crisis_rate = models.FloatField()
    
    # Demographics (anonymized percentages)
    age_distribution = models.JSONField(default=dict)
    user_type_distribution = models.JSONField(default=dict)
    
    # Engagement
    average_sessions_per_user = models.FloatField()
    resource_usage = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'regional_mental_health_trends'
        unique_together = ['region', 'country', 'year', 'month']
        ordering = ['-year', '-month']


# ========================
# CONTENT MODERATION
# ========================

class ContentModerationLog(models.Model):
    """Log of all moderation actions"""
    ACTION_TYPES = [
        ('approve', 'Approved'),
        ('flag', 'Flagged'),
        ('remove', 'Removed'),
        ('warn', 'Warning Issued'),
        ('ban', 'User Banned'),
    ]
    
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderation_actions')
    
    # Content being moderated
    forum_post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, null=True, blank=True)
    forum_reply = models.ForeignKey(ForumReply, on_delete=models.CASCADE, null=True, blank=True)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True)
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    reason = models.TextField()
    notes = models.TextField(blank=True)
    
    # AI assistance
    ai_suggested = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_moderation_logs'
        ordering = ['-created_at']


# ========================
# SYSTEM CONFIGURATION
# ========================

class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField()
    
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'system_configuration'


class AuditLog(models.Model):
    """Audit trail for security and compliance"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]