from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    User, UserProfile, EmergencyContact,
    TherapistProfile, TherapistAvailability,
    ChatSession, ChatMessage, BotResponse,
    MoodEntry, MoodPattern,
    CrisisAlert, CrisisResource,
    ForumCategory, ForumPost, ForumReply, ForumLike, ForumReport,
    CounselingAppointment, SessionNote, TherapistReview,
    Resource, UserResourceInteraction, AIRecommendation,
    WellnessActivity, UserActivityLog, JournalEntry,
    Notification,
    Achievement, UserAchievement, UserStreak,
    PlatformAnalytics, RegionalMentalHealthTrend,
    ContentModerationLog,
    SystemConfiguration, AuditLog
)


# ========================
# USER MANAGEMENT
# ========================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0
    fields = ('name', 'relationship', 'phone_number', 'email', 'is_primary', 'can_be_contacted_during_crisis')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'country', 'is_verified', 'is_active', 'created_at', 'account_status')
    list_filter = ('user_type', 'is_verified', 'is_active', 'account_suspended', 'country', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)  # Fixed: Changed from ('-year', '-month') to ('-created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name')
        }),
        ('User Type & Demographics', {
            'fields': ('user_type', 'date_of_birth', 'gender', 'phone_number', 'country', 'region')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'timezone')
        }),
        ('Privacy', {
            'fields': ('is_anonymous', 'data_sharing_consent')
        }),
        ('Account Status', {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'account_suspended', 'suspension_reason')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'last_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    inlines = [UserProfileInline, EmergencyContactInline]
    
    actions = ['verify_users', 'suspend_users', 'activate_users']
    
    def account_status(self, obj):
        if obj.account_suspended:
            return format_html('<span style="color: red;">⛔ Suspended</span>')
        elif obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Unverified</span>')
    
    account_status.short_description = 'Status'
    
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} users verified successfully.')
    
    verify_users.short_description = 'Verify selected users'
    
    def suspend_users(self, request, queryset):
        queryset.update(account_suspended=True, is_active=False)
        self.message_user(request, f'{queryset.count()} users suspended.')
    
    suspend_users.short_description = 'Suspend selected users'
    
    def activate_users(self, request, queryset):
        queryset.update(account_suspended=False, is_active=True)
        self.message_user(request, f'{queryset.count()} users activated.')
    
    activate_users.short_description = 'Activate selected users'


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'relationship', 'phone_number', 'is_primary', 'can_be_contacted_during_crisis')
    list_filter = ('is_primary', 'can_be_contacted_during_crisis', 'relationship')
    search_fields = ('name', 'user__username', 'user__email', 'phone_number')
    ordering = ('-is_primary', 'name')


# ========================
# THERAPIST MANAGEMENT
# ========================

class TherapistAvailabilityInline(admin.TabularInline):
    model = TherapistAvailability
    extra = 0


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'years_of_experience', 'is_verified', 'available_for_sessions', 'average_rating', 'total_sessions')
    list_filter = ('is_verified', 'available_for_sessions', 'accepts_insurance', 'created_at')
    search_fields = ('user__username', 'user__email', 'license_number', 'practice_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Therapist Info', {
            'fields': ('user', 'license_number', 'specializations', 'years_of_experience')
        }),
        ('Credentials', {
            'fields': ('education', 'certifications')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_documents', 'verified_at', 'verified_by')
        }),
        ('Practice Details', {
            'fields': ('practice_name', 'practice_address', 'consultation_fee', 'accepts_insurance', 'languages_spoken')
        }),
        ('Availability', {
            'fields': ('available_for_sessions', 'max_clients')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_sessions'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('average_rating', 'total_sessions', 'verified_at')
    
    inlines = [TherapistAvailabilityInline]
    
    actions = ['verify_therapists', 'make_available', 'make_unavailable']
    
    def verify_therapists(self, request, queryset):
        queryset.update(is_verified=True, verified_at=timezone.now(), verified_by=request.user)
        self.message_user(request, f'{queryset.count()} therapists verified.')
    
    verify_therapists.short_description = 'Verify selected therapists'
    
    def make_available(self, request, queryset):
        queryset.update(available_for_sessions=True)
        self.message_user(request, f'{queryset.count()} therapists set to available.')
    
    make_available.short_description = 'Make available for sessions'
    
    def make_unavailable(self, request, queryset):
        queryset.update(available_for_sessions=False)
        self.message_user(request, f'{queryset.count()} therapists set to unavailable.')
    
    make_unavailable.short_description = 'Make unavailable for sessions'


# ========================
# AI CHATBOT
# ========================

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ('sender', 'message_text', 'sentiment_score', 'requires_intervention', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'crisis_detected', 'crisis_severity', 'total_messages', 'started_at', 'duration')
    list_filter = ('status', 'crisis_detected', 'crisis_handled', 'started_at')
    search_fields = ('user__username', 'user__email', 'id')
    ordering = ('-started_at',)
    
    fieldsets = (
        ('Session Info', {
            'fields': ('user', 'session_title', 'status', 'ai_model_version', 'therapy_framework')
        }),
        ('Crisis Tracking', {
            'fields': ('crisis_detected', 'crisis_severity', 'crisis_handled'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('started_at', 'ended_at', 'total_messages')
        }),
    )
    
    readonly_fields = ('started_at',)
    
    inlines = [ChatMessageInline]
    
    def duration(self, obj):
        if obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return f"{duration.seconds // 60} min"
        return "Ongoing"
    
    duration.short_description = 'Duration'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'message_preview', 'sentiment_score', 'requires_intervention', 'is_flagged', 'created_at')
    list_filter = ('sender', 'requires_intervention', 'is_flagged', 'contains_crisis_keywords', 'created_at')
    search_fields = ('message_text', 'session__user__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Message Info', {
            'fields': ('session', 'sender', 'message_text')
        }),
        ('AI Analysis', {
            'fields': ('sentiment_score', 'emotion_detected', 'intent_classification', 'keywords_extracted')
        }),
        ('Crisis Detection', {
            'fields': ('contains_crisis_keywords', 'suicide_risk_score', 'requires_intervention'),
            'classes': ('collapse',)
        }),
        ('Moderation', {
            'fields': ('is_flagged', 'flagged_reason')
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message_text[:50] + '...' if len(obj.message_text) > 50 else obj.message_text
    
    message_preview.short_description = 'Message'


# ========================
# MOOD TRACKING
# ========================

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_date', 'mood_level', 'mood_score', 'energy_level', 'sleep_quality', 'created_at')
    list_filter = ('mood_level', 'entry_date', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-entry_date',)
    date_hierarchy = 'entry_date'
    
    fieldsets = (
        ('User & Date', {
            'fields': ('user', 'entry_date')
        }),
        ('Mood Data', {
            'fields': ('mood_level', 'mood_score', 'emotions', 'energy_level')
        }),
        ('Sleep', {
            'fields': ('sleep_quality', 'sleep_hours')
        }),
        ('Context', {
            'fields': ('activities', 'triggers', 'notes', 'location', 'weather')
        }),
    )


@admin.register(MoodPattern)
class MoodPatternAdmin(admin.ModelAdmin):
    list_display = ('user', 'period_type', 'start_date', 'end_date', 'average_mood_score', 'trend_direction', 'concern_level')
    list_filter = ('period_type', 'trend_direction', 'concern_level', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-end_date',)


# ========================
# CRISIS MANAGEMENT
# ========================

@admin.register(CrisisAlert)
class CrisisAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'severity', 'status', 'crisis_type', 'ai_confidence_score', 'emergency_services_contacted', 'detected_at', 'time_to_response')
    list_filter = ('severity', 'status', 'crisis_type', 'emergency_services_contacted', 'detected_at')
    search_fields = ('user__username', 'user__email', 'crisis_type')
    ordering = ('-detected_at',)
    date_hierarchy = 'detected_at'
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('user', 'severity', 'status', 'crisis_type')
        }),
        ('Detection Source', {
            'fields': ('chat_session', 'mood_entry')
        }),
        ('Detection Data', {
            'fields': ('triggering_content', 'ai_confidence_score', 'keywords_matched')
        }),
        ('Response', {
            'fields': ('intervention_taken', 'responder', 'emergency_services_contacted', 'emergency_contact_notified')
        }),
        ('Timestamps', {
            'fields': ('detected_at', 'acknowledged_at', 'resolved_at')
        }),
    )
    
    readonly_fields = ('detected_at',)
    
    actions = ['mark_as_acknowledged', 'mark_as_resolved']
    
    def time_to_response(self, obj):
        if obj.acknowledged_at:
            diff = obj.acknowledged_at - obj.detected_at
            minutes = diff.seconds // 60
            return f"{minutes} min"
        return "Not responded"
    
    time_to_response.short_description = 'Response Time'
    
    def mark_as_acknowledged(self, request, queryset):
        queryset.update(status='acknowledged', acknowledged_at=timezone.now())
        self.message_user(request, f'{queryset.count()} alerts acknowledged.')
    
    mark_as_acknowledged.short_description = 'Mark as acknowledged'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} alerts resolved.')
    
    mark_as_resolved.short_description = 'Mark as resolved'


@admin.register(CrisisResource)
class CrisisResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'resource_type', 'phone_number', 'available_24_7', 'is_active')
    list_filter = ('country', 'resource_type', 'available_24_7', 'is_active')
    search_fields = ('name', 'country', 'region', 'phone_number')
    ordering = ('country', 'name')


# ========================
# COMMUNITY FORUM
# ========================

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'post_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    
    def post_count(self, obj):
        return obj.posts.count()
    
    post_count.short_description = 'Posts'


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_anonymous', 'view_count', 'like_count', 'reply_count', 'moderation_status', 'is_published', 'created_at')
    list_filter = ('category', 'is_anonymous', 'is_published', 'is_pinned', 'is_locked', 'moderation_status', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Post Info', {
            'fields': ('category', 'author', 'title', 'content', 'is_anonymous')
        }),
        ('Engagement', {
            'fields': ('view_count', 'like_count', 'reply_count')
        }),
        ('Moderation', {
            'fields': ('is_published', 'is_pinned', 'is_locked', 'is_flagged', 'moderation_status')
        }),
        ('AI Analysis', {
            'fields': ('toxicity_score', 'sentiment_score', 'ai_flagged'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'like_count', 'reply_count')
    
    actions = ['publish_posts', 'unpublish_posts', 'pin_posts', 'lock_posts']
    
    def publish_posts(self, request, queryset):
        queryset.update(is_published=True, moderation_status='approved')
        self.message_user(request, f'{queryset.count()} posts published.')
    
    publish_posts.short_description = 'Publish selected posts'
    
    def unpublish_posts(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f'{queryset.count()} posts unpublished.')
    
    unpublish_posts.short_description = 'Unpublish selected posts'
    
    def pin_posts(self, request, queryset):
        queryset.update(is_pinned=True)
        self.message_user(request, f'{queryset.count()} posts pinned.')
    
    pin_posts.short_description = 'Pin selected posts'
    
    def lock_posts(self, request, queryset):
        queryset.update(is_locked=True)
        self.message_user(request, f'{queryset.count()} posts locked.')
    
    lock_posts.short_description = 'Lock selected posts'


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_anonymous', 'like_count', 'is_published', 'is_flagged', 'created_at')
    list_filter = ('is_anonymous', 'is_published', 'is_flagged', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')
    ordering = ('-created_at',)


@admin.register(ForumReport)
class ForumReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reason', 'status', 'reviewed_by', 'content_link', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('reporter__username', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Report Info', {
            'fields': ('reporter', 'post', 'reply', 'reason', 'description')
        }),
        ('Moderation', {
            'fields': ('status', 'reviewed_by', 'action_taken', 'reviewed_at')
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def content_link(self, obj):
        if obj.post:
            return format_html('<a href="{}">Post: {}</a>', 
                             reverse('admin:web_application_forumpost_change', args=[obj.post.id]),
                             obj.post.title[:30])
        elif obj.reply:
            return format_html('<a href="{}">Reply</a>',
                             reverse('admin:web_application_forumreply_change', args=[obj.reply.id]))
        return '-'
    
    content_link.short_description = 'Content'


# ========================
# COUNSELING
# ========================

@admin.register(CounselingAppointment)
class CounselingAppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'therapist', 'session_type', 'scheduled_date', 'scheduled_time', 'status', 'payment_status', 'attended')
    list_filter = ('status', 'session_type', 'payment_status', 'scheduled_date', 'attended')
    search_fields = ('client__username', 'therapist__user__username')
    ordering = ('-scheduled_date', '-scheduled_time')
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Appointment Info', {
            'fields': ('client', 'therapist', 'session_type', 'scheduled_date', 'scheduled_time', 'duration_minutes')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
        ('Session Details', {
            'fields': ('meeting_link', 'meeting_id', 'notes_for_therapist')
        }),
        ('Payment', {
            'fields': ('fee',)
        }),
        ('Post-Session', {
            'fields': ('attended', 'session_notes', 'next_session_recommended')
        }),
    )
    
    actions = ['confirm_appointments', 'mark_completed']
    
    def confirm_appointments(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} appointments confirmed.')
    
    confirm_appointments.short_description = 'Confirm selected appointments'
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed', attended=True)
        self.message_user(request, f'{queryset.count()} appointments marked as completed.')
    
    mark_completed.short_description = 'Mark as completed'


@admin.register(TherapistReview)
class TherapistReviewAdmin(admin.ModelAdmin):
    list_display = ('therapist', 'client', 'rating', 'professionalism', 'effectiveness', 'empathy', 'would_recommend', 'is_published', 'created_at')
    list_filter = ('rating', 'would_recommend', 'is_published', 'is_anonymous', 'created_at')
    search_fields = ('therapist__user__username', 'client__username', 'review_text')
    ordering = ('-created_at',)


# ========================
# RESOURCES
# ========================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'language', 'view_count', 'like_count', 'average_rating', 'is_featured', 'is_published', 'created_at')
    list_filter = ('resource_type', 'language', 'is_featured', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'author', 'tags')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'resource_type', 'description', 'author', 'source')
        }),
        ('Content', {
            'fields': ('content', 'file_url', 'video_url', 'audio_url', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('duration_minutes', 'difficulty_level', 'tags', 'target_audience', 'mental_health_topics')
        }),
        ('Language', {
            'fields': ('language', 'translations_available')
        }),
        ('Engagement', {
            'fields': ('view_count', 'like_count', 'share_count', 'average_rating')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_published')
        }),
    )
    
    readonly_fields = ('view_count', 'like_count', 'share_count', 'average_rating')
    
    actions = ['feature_resources', 'publish_resources']
    
    def feature_resources(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} resources featured.')
    
    feature_resources.short_description = 'Feature selected resources'
    
    def publish_resources(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, f'{queryset.count()} resources published.')
    
    publish_resources.short_description = 'Publish selected resources'


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'title', 'confidence_score', 'priority', 'viewed', 'acted_upon', 'dismissed', 'created_at')
    list_filter = ('recommendation_type', 'viewed', 'acted_upon', 'dismissed', 'created_at')
    search_fields = ('user__username', 'title', 'description')
    ordering = ('-priority', '-created_at')


# ========================
# WELLNESS ACTIVITIES
# ========================

@admin.register(WellnessActivity)
class WellnessActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_type', 'duration_minutes', 'difficulty', 'is_active', 'completion_count')
    list_filter = ('activity_type', 'difficulty', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('activity_type', 'title')
    
    def completion_count(self, obj):
        return obj.completion_logs.filter(completed=True).count()
    
    completion_count.short_description = 'Completions'


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'mood_score', 'sentiment_score', 'is_private', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('user__username', 'title', 'content')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# ========================
# NOTIFICATIONS
# ========================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'priority', 'is_read', 'is_archived', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_archived', 'priority', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{queryset.count()} notifications marked as read.')
    
    mark_as_read.short_description = 'Mark as read'


# ========================
# GAMIFICATION
# ========================

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'requirement_type', 'requirement_count', 'points', 'is_active', 'earned_count')
    list_filter = ('requirement_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('requirement_type', 'requirement_count')
    
    def earned_count(self, obj):
        return obj.earned_by.count()
    
    earned_count.short_description = 'Earned By'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__name')
    ordering = ('-earned_at',)


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_mood_streak', 'longest_mood_streak', 'current_activity_streak', 'total_points', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username',)
    ordering = ('-total_points',)


# ========================
# ANALYTICS
# ========================

@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'new_users', 'active_users', 'crisis_alerts', 'total_appointments', 'average_mood_score')
    list_filter = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('User Metrics', {
            'fields': ('total_users', 'new_users', 'active_users')
        }),
        ('Engagement', {
            'fields': ('total_chat_sessions', 'total_messages', 'total_mood_entries', 'total_forum_posts')
        }),
        ('Crisis', {
            'fields': ('crisis_alerts', 'crisis_interventions')
        }),
        ('Professional Services', {
            'fields': ('total_appointments', 'completed_appointments')
        }),
        ('Geographic Data', {
            'fields': ('users_by_country', 'users_by_age_group'),
            'classes': ('collapse',)
        }),
        ('Sentiment', {
            'fields': ('average_mood_score', 'average_sentiment')
        }),
    )


@admin.register(RegionalMentalHealthTrend)
class RegionalMentalHealthTrendAdmin(admin.ModelAdmin):
    list_display = ('country', 'region', 'year', 'month', 'total_users', 'average_mood_score', 'crisis_rate')
    list_filter = ('country', 'year', 'month')
    search_fields = ('country', 'region')
    ordering = ('-year', '-month')
    
    # Fixed: Removed incorrect fieldsets and inlines
    fieldsets = (
        ('Location & Time', {
            'fields': ('country', 'region', 'year', 'month')
        }),
        ('User Metrics', {
            'fields': ('total_users', 'active_users', 'new_users')
        }),
        ('Mental Health Metrics', {
            'fields': ('average_mood_score', 'crisis_alerts_count', 'crisis_rate')
        }),
        ('Engagement', {
            'fields': ('total_chat_sessions', 'total_mood_entries', 'total_appointments')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


# ========================
# CONTENT MODERATION
# ========================

@admin.register(ContentModerationLog)
class ContentModerationLogAdmin(admin.ModelAdmin):
    list_display = ('moderator', 'action_type', 'content_type', 'ai_suggested', 'ai_confidence', 'created_at')
    list_filter = ('action_type', 'ai_suggested', 'created_at')
    search_fields = ('moderator__username', 'reason', 'notes')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Moderation Info', {
            'fields': ('moderator', 'action_type', 'reason', 'notes')
        }),
        ('Content', {
            'fields': ('forum_post', 'forum_reply', 'chat_message')
        }),
        ('AI Assistance', {
            'fields': ('ai_suggested', 'ai_confidence')
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def content_type(self, obj):
        if obj.forum_post:
            return format_html('<span style="color: blue;">Forum Post</span>')
        elif obj.forum_reply:
            return format_html('<span style="color: green;">Forum Reply</span>')
        elif obj.chat_message:
            return format_html('<span style="color: orange;">Chat Message</span>')
        return '-'
    
    content_type.short_description = 'Content Type'


# ========================
# SYSTEM CONFIGURATION
# ========================

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'is_active', 'updated_at', 'updated_by')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('updated_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'ip_address', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'action', 'model_name', 'object_id', 'ip_address')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('User & Action', {
            'fields': ('user', 'action', 'model_name', 'object_id')
        }),
        ('Changes', {
            'fields': ('changes',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'timestamp')
        }),
    )
    
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ========================
# CUSTOM ADMIN SITE
# ========================

class MentalHealthAdminSite(admin.AdminSite):
    site_header = 'Mental Health Platform Administration'
    site_title = 'Mental Health Admin'
    index_title = 'Platform Management Dashboard'
    
    def index(self, request, extra_context=None):
        """Custom admin index with statistics."""
        extra_context = extra_context or {}
        
        # Get statistics
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        
        # User stats
        total_users = User.objects.count()
        active_users_week = User.objects.filter(last_active__gte=last_week).count()
        new_users_week = User.objects.filter(created_at__gte=last_week).count()
        
        # Crisis stats
        active_crises = CrisisAlert.objects.filter(
            status__in=['detected', 'acknowledged']
        ).count()
        crises_week = CrisisAlert.objects.filter(detected_at__gte=last_week).count()
        
        # Engagement stats
        chat_sessions_today = ChatSession.objects.filter(started_at__date=today).count()
        mood_entries_today = MoodEntry.objects.filter(entry_date=today).count()
        
        # Moderation stats
        pending_reports = ForumReport.objects.filter(status='pending').count()
        flagged_posts = ForumPost.objects.filter(is_flagged=True, is_published=True).count()
        
        # Appointment stats
        upcoming_appointments = CounselingAppointment.objects.filter(
            scheduled_date__gte=today,
            status='confirmed'
        ).count()
        
        extra_context.update({
            'statistics': {
                'users': {
                    'total': total_users,
                    'active_week': active_users_week,
                    'new_week': new_users_week,
                },
                'crisis': {
                    'active': active_crises,
                    'week': crises_week,
                },
                'engagement': {
                    'chat_sessions_today': chat_sessions_today,
                    'mood_entries_today': mood_entries_today,
                },
                'moderation': {
                    'pending_reports': pending_reports,
                    'flagged_posts': flagged_posts,
                },
                'appointments': {
                    'upcoming': upcoming_appointments,
                }
            }
        })
        
        return super().index(request, extra_context)


# Uncomment to use custom admin site
# admin_site = MentalHealthAdminSite(name='mentalhealth_admin')


# ========================
# ADDITIONAL INLINES
# ========================

class UserAchievementInline(admin.TabularInline):
    model = UserAchievement
    extra = 0
    fields = ('achievement', 'earned_at')
    readonly_fields = ('earned_at',)
    can_delete = False


class TherapistReviewInline(admin.TabularInline):
    model = TherapistReview
    extra = 0
    fields = ('client', 'rating', 'professionalism', 'effectiveness', 'empathy', 'would_recommend', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


# ========================
# REGISTER REMAINING MODELS
# ========================

# Register models that don't need custom admin
admin.site.register(UserProfile)
admin.site.register(BotResponse)
admin.site.register(UserActivityLog)
admin.site.register(UserResourceInteraction)
admin.site.register(ForumLike)
admin.site.register(SessionNote)


# ========================
# ADMIN ACTIONS
# ========================

def export_as_csv(modeladmin, request, queryset):
    """Generic CSV export action."""
    import csv
    from django.http import HttpResponse
    
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)
    
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    
    return response

export_as_csv.short_description = "Export Selected as CSV"


# Add export action to all admins
def register_export_action():
    """Register export action for all model admins."""
    for model, model_admin in admin.site._registry.items():
        if hasattr(model_admin, 'actions'):
            if model_admin.actions is None:
                model_admin.actions = []
            if export_as_csv not in model_admin.actions:
                model_admin.actions.append(export_as_csv)

# Uncomment to enable CSV export for all models
# register_export_action()


# ========================
# CUSTOM FILTERS
# ========================

class CrisisLevelFilter(admin.SimpleListFilter):
    title = 'crisis level'
    parameter_name = 'crisis_level'
    
    def lookups(self, request, model_admin):
        return (
            ('high', 'High Risk (8-10)'),
            ('medium', 'Medium Risk (5-7)'),
            ('low', 'Low Risk (1-4)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(crisis_severity__gte=8)
        if self.value() == 'medium':
            return queryset.filter(crisis_severity__gte=5, crisis_severity__lt=8)
        if self.value() == 'low':
            return queryset.filter(crisis_severity__lt=5)


class RecentActivityFilter(admin.SimpleListFilter):
    title = 'recent activity'
    parameter_name = 'recent'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=today)
        if self.value() == 'week':
            week_ago = today - timedelta(days=7)
            return queryset.filter(created_at__date__gte=week_ago)
        if self.value() == 'month':
            month_ago = today - timedelta(days=30)
            return queryset.filter(created_at__date__gte=month_ago)


# ========================
# ADMIN DASHBOARD WIDGETS
# ========================

class DashboardStats:
    """Helper class for dashboard statistics."""
    
    @staticmethod
    def get_user_growth():
        """Get user growth statistics."""
        from django.db.models.functions import TruncDate
        
        last_30_days = timezone.now() - timedelta(days=30)
        users = User.objects.filter(created_at__gte=last_30_days).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return list(users)
    
    @staticmethod
    def get_crisis_alerts_summary():
        """Get crisis alerts summary."""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        return {
            'today': CrisisAlert.objects.filter(detected_at__date=today).count(),
            'week': CrisisAlert.objects.filter(detected_at__date__gte=week_ago).count(),
            'active': CrisisAlert.objects.filter(
                status__in=['detected', 'acknowledged']
            ).count(),
        }
    
    @staticmethod
    def get_mood_trends():
        """Get average mood trends."""
        last_7_days = timezone.now().date() - timedelta(days=7)
        
        moods = MoodEntry.objects.filter(
            entry_date__gte=last_7_days
        ).values('entry_date').annotate(
            avg_score=Avg('mood_score')
        ).order_by('entry_date')
        
        return list(moods)
    
    @staticmethod
    def get_engagement_metrics():
        """Get engagement metrics."""
        today = timezone.now().date()
        
        return {
            'chat_sessions': ChatSession.objects.filter(started_at__date=today).count(),
            'mood_entries': MoodEntry.objects.filter(entry_date=today).count(),
            'forum_posts': ForumPost.objects.filter(created_at__date=today).count(),
            'active_users': User.objects.filter(last_active__date=today).count(),
        }


# ========================
# READONLY FIELDS HELPERS
# ========================

def make_readonly(modeladmin):
    """Helper to make all fields readonly."""
    modeladmin.readonly_fields = [f.name for f in modeladmin.model._meta.fields]
    return modeladmin


# ========================
# ADMIN PERMISSIONS
# ========================

class ViewOnlyMixin:
    """Mixin to make admin view-only."""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Apply ViewOnlyMixin to sensitive models if needed
# class SensitiveModelAdmin(ViewOnlyMixin, admin.ModelAdmin):
#     pass


# ========================
# ADMIN SITE CUSTOMIZATION
# ========================

# Customize admin site
admin.site.site_header = "Mental Health Platform Administration"
admin.site.site_title = "Mental Health Admin Portal"
admin.site.index_title = "Welcome to Mental Health Platform Administration"

# Add custom CSS/JS
# class CustomAdminSite(admin.AdminSite):
#     class Media:
#         css = {
#             'all': ('admin/css/custom_admin.css',)
#         }
#         js = ('admin/js/custom_admin.js',)