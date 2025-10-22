from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta, time, date
from decimal import Decimal
import random
import json

from web_application.models import (
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


class Command(BaseCommand):
    help = 'Seeds the database with realistic test data for mental health platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Seed in order of dependencies
        self.seed_users()
        self.seed_emergency_contacts()
        self.seed_therapist_profiles()
        self.seed_therapist_availability()
        self.seed_chat_sessions()
        self.seed_mood_entries()
        self.seed_mood_patterns()
        self.seed_crisis_alerts()
        self.seed_crisis_resources()
        self.seed_forum_categories()
        self.seed_forum_posts()
        self.seed_forum_replies()
        self.seed_forum_likes()
        self.seed_forum_reports()
        self.seed_counseling_appointments()
        self.seed_session_notes()
        self.seed_therapist_reviews()
        self.seed_resources()
        self.seed_user_resource_interactions()
        self.seed_ai_recommendations()
        self.seed_wellness_activities()
        self.seed_user_activity_logs()
        self.seed_journal_entries()
        self.seed_notifications()
        self.seed_achievements()
        self.seed_user_achievements()
        self.seed_user_streaks()
        self.seed_platform_analytics()
        self.seed_regional_trends()
        self.seed_content_moderation_logs()
        self.seed_system_configuration()
        self.seed_audit_logs()

        self.stdout.write(self.style.SUCCESS('✅ Data seeding completed successfully!'))

    def clear_data(self):
        """Clear all existing data"""
        models = [
            AuditLog, SystemConfiguration, ContentModerationLog,
            RegionalMentalHealthTrend, PlatformAnalytics,
            UserStreak, UserAchievement, Achievement,
            Notification, JournalEntry, UserActivityLog, WellnessActivity,
            AIRecommendation, UserResourceInteraction, Resource,
            TherapistReview, SessionNote, CounselingAppointment,
            ForumReport, ForumLike, ForumReply, ForumPost, ForumCategory,
            CrisisResource, CrisisAlert,
            MoodPattern, MoodEntry,
            BotResponse, ChatMessage, ChatSession,
            TherapistAvailability, TherapistProfile,
            EmergencyContact, UserProfile, User,
        ]
        
        for model in models:
            model.objects.all().delete()
            self.stdout.write(f'  Cleared {model.__name__}')

    def seed_users(self):
        """Seed users with different types"""
        self.stdout.write('Seeding users...')
        
        countries = ['Kenya', 'Uganda', 'Tanzania', 'Nigeria', 'South Africa', 'USA', 'UK', 'Canada']
        users_data = []

        # Admin user
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@mentalhealth.com',
            password='admin123',
            user_type='admin',
            country='Kenya',
            is_verified=True
        )
        users_data.append(admin)

        # Moderators
        for i in range(3):
            mod = User.objects.create(
                username=f'moderator{i+1}',
                email=f'moderator{i+1}@mentalhealth.com',
                password=make_password('password123'),
                user_type='moderator',
                first_name=f'Moderator',
                last_name=f'{i+1}',
                country=random.choice(countries),
                is_verified=True,
                is_staff=True
            )
            users_data.append(mod)

        # Therapists
        therapist_names = [
            ('Dr. Sarah', 'Johnson'), ('Dr. Michael', 'Chen'),
            ('Dr. Amara', 'Okafor'), ('Dr. James', 'Thompson'),
            ('Dr. Fatima', 'Hassan'), ('Dr. David', 'Kimani'),
            ('Dr. Grace', 'Mwangi'), ('Dr. Peter', 'Omondi')
        ]
        
        for first, last in therapist_names:
            therapist = User.objects.create(
                username=f'{first.lower()}.{last.lower()}',
                email=f'{first.lower()}.{last.lower()}@therapy.com',
                password=make_password('password123'),
                user_type='therapist',
                first_name=first,
                last_name=last,
                country=random.choice(countries),
                phone_number=f'+254{random.randint(700000000, 799999999)}',
                gender=random.choice(['male', 'female']),
                is_verified=True,
                date_of_birth=date(random.randint(1970, 1990), random.randint(1, 12), random.randint(1, 28))
            )
            users_data.append(therapist)

        # Students
        for i in range(30):
            student = User.objects.create(
                username=f'student{i+1}',
                email=f'student{i+1}@university.edu',
                password=make_password('password123'),
                user_type='student',
                first_name=f'Student{i+1}',
                last_name=f'User{i+1}',
                country=random.choice(countries),
                region=random.choice(['Nairobi', 'Kampala', 'Dar es Salaam', 'Lagos', 'Cape Town']),
                phone_number=f'+254{random.randint(700000000, 799999999)}',
                gender=random.choice(['male', 'female', 'non_binary', 'prefer_not_to_say']),
                is_verified=random.choice([True, False]),
                date_of_birth=date(random.randint(1995, 2005), random.randint(1, 12), random.randint(1, 28)),
                last_active=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            users_data.append(student)
            
            # Create user profile
            UserProfile.objects.create(
                user=student,
                bio=f'I am a student studying at university. Interested in mental health and wellbeing.',
                university=random.choice(['University of Nairobi', 'Makerere University', 'University of Dar es Salaam', 'University of Lagos']),
                field_of_study=random.choice(['Computer Science', 'Psychology', 'Business', 'Engineering', 'Medicine', 'Arts']),
                academic_year=random.choice(['First Year', 'Second Year', 'Third Year', 'Fourth Year']),
                has_previous_therapy=random.choice([True, False]),
                notification_preferences={
                    'email': True,
                    'push': True,
                    'sms': False
                }
            )

        # Adults
        for i in range(20):
            adult = User.objects.create(
                username=f'adult{i+1}',
                email=f'adult{i+1}@email.com',
                password=make_password('password123'),
                user_type='adult',
                first_name=f'Adult{i+1}',
                last_name=f'User{i+1}',
                country=random.choice(countries),
                phone_number=f'+254{random.randint(700000000, 799999999)}',
                gender=random.choice(['male', 'female', 'non_binary']),
                is_verified=True,
                date_of_birth=date(random.randint(1970, 1995), random.randint(1, 12), random.randint(1, 28)),
                last_active=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            users_data.append(adult)
            
            UserProfile.objects.create(
                user=adult,
                bio='Adult user seeking mental health support.',
                has_previous_therapy=random.choice([True, False]),
                notification_preferences={'email': True, 'push': True}
            )

        self.users = users_data
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(users_data)} users'))

    def seed_emergency_contacts(self):
        """Seed emergency contacts for users"""
        self.stdout.write('Seeding emergency contacts...')
        
        count = 0
        for user in User.objects.filter(user_type__in=['student', 'adult', 'child']):
            # Primary contact
            EmergencyContact.objects.create(
                user=user,
                name=f'{user.first_name} Parent',
                relationship='Parent',
                phone_number=f'+254{random.randint(700000000, 799999999)}',
                email=f'parent.{user.username}@email.com',
                is_primary=True,
                can_be_contacted_during_crisis=True
            )
            count += 1
            
            # Secondary contact (50% chance)
            if random.random() > 0.5:
                EmergencyContact.objects.create(
                    user=user,
                    name=f'{user.first_name} Friend',
                    relationship='Friend',
                    phone_number=f'+254{random.randint(700000000, 799999999)}',
                    email=f'friend.{user.username}@email.com',
                    is_primary=False,
                    can_be_contacted_during_crisis=True
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} emergency contacts'))

    def seed_therapist_profiles(self):
        """Seed therapist profiles"""
        self.stdout.write('Seeding therapist profiles...')
        
        therapists = User.objects.filter(user_type='therapist')
        specializations_options = [
            ['clinical_psychology', 'cbt'],
            ['counseling', 'trauma'],
            ['child_psychology', 'family_therapy'],
            ['psychiatry', 'addiction'],
            ['cbt', 'trauma']
        ]
        
        count = 0
        for therapist in therapists:
            TherapistProfile.objects.create(
                user=therapist,
                license_number=f'LIC{random.randint(10000, 99999)}',
                specializations=random.choice(specializations_options),
                years_of_experience=random.randint(5, 25),
                education=f'PhD in Clinical Psychology from {random.choice(["Harvard", "Stanford", "Oxford", "Cambridge"])}',
                certifications='Licensed Clinical Psychologist, CBT Certified',
                is_verified=True,
                verified_at=timezone.now() - timedelta(days=random.randint(30, 365)),
                verified_by=User.objects.filter(user_type='admin').first(),
                practice_name=f'{therapist.first_name} {therapist.last_name} Therapy Practice',
                consultation_fee=Decimal(random.randint(50, 200)),
                accepts_insurance=random.choice([True, False]),
                languages_spoken=['English', 'Swahili'] if therapist.country in ['Kenya', 'Uganda', 'Tanzania'] else ['English'],
                available_for_sessions=True,
                max_clients=random.randint(15, 30),
                average_rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.01')),
                total_sessions=random.randint(50, 500)
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} therapist profiles'))

    def seed_therapist_availability(self):
        """Seed therapist availability schedules"""
        self.stdout.write('Seeding therapist availability...')
        
        count = 0
        for profile in TherapistProfile.objects.all():
            # Weekday availability (Monday-Friday)
            for day in range(5):
                # Morning slot
                TherapistAvailability.objects.create(
                    therapist=profile,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(12, 0),
                    is_available=True
                )
                # Afternoon slot
                TherapistAvailability.objects.create(
                    therapist=profile,
                    day_of_week=day,
                    start_time=time(14, 0),
                    end_time=time(17, 0),
                    is_available=True
                )
                count += 2
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} availability slots'))

    def seed_chat_sessions(self):
        """Seed chat sessions"""
        self.stdout.write('Seeding chat sessions...')
        
        users = User.objects.filter(user_type__in=['student', 'adult'])
        count = 0
        
        for user in users[:30]:
            # Create 1-5 sessions per user
            for _ in range(random.randint(1, 5)):
                started = timezone.now() - timedelta(days=random.randint(0, 90))
                status = random.choice(['active', 'ended', 'ended', 'ended'])
                
                session = ChatSession.objects.create(
                    user=user,
                    session_title=random.choice([
                        'Feeling anxious about exams',
                        'Having trouble sleeping',
                        'Stress management',
                        'Daily check-in',
                        'Need someone to talk to'
                    ]),
                    status=status,
                    ai_model_version='GPT-4-Mental-Health-v1',
                    therapy_framework=random.choice(['CBT', 'DBT', 'Mindfulness', 'Solution-Focused']),
                    started_at=started,
                    ended_at=started + timedelta(minutes=random.randint(10, 60)) if status == 'ended' else None,
                    total_messages=random.randint(5, 50),
                    crisis_detected=random.choice([False, False, False, True]),
                    crisis_severity=random.randint(1, 10) if random.random() > 0.8 else None
                )
                
                # Create messages for the session
                self.seed_chat_messages(session)
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} chat sessions'))

    def seed_chat_messages(self, session):
        """Seed messages for a chat session"""
        num_messages = random.randint(5, 20)
        
        user_messages = [
            "I've been feeling really anxious lately",
            "I can't seem to focus on my studies",
            "I'm having trouble sleeping at night",
            "Everyone seems to be doing better than me",
            "I feel overwhelmed with everything",
            "Thank you, that's helpful",
            "I'll try that technique",
            "Can you tell me more about CBT?",
        ]
        
        bot_messages = [
            "I hear that you're feeling anxious. Can you tell me more about what's been triggering these feelings?",
            "It's completely normal to feel this way. Let's explore some coping strategies together.",
            "Have you tried any relaxation techniques like deep breathing?",
            "Remember that everyone's journey is different, and it's okay to go at your own pace.",
            "Let me share a helpful resource about managing anxiety.",
            "Would you like to try a quick mindfulness exercise?",
        ]
        
        for i in range(num_messages):
            sender = 'user' if i % 2 == 0 else 'bot'
            message = random.choice(user_messages if sender == 'user' else bot_messages)
            
            msg = ChatMessage.objects.create(
                session=session,
                sender=sender,
                message_text=message,
                sentiment_score=random.uniform(-1, 1),
                emotion_detected={'primary': random.choice(['anxious', 'sad', 'neutral', 'happy'])},
                keywords_extracted=['anxiety', 'stress', 'sleep'] if sender == 'user' else [],
                contains_crisis_keywords=random.choice([False, False, False, True]),
                suicide_risk_score=random.uniform(0, 1) if random.random() > 0.9 else None,
                requires_intervention=random.choice([False, False, False, True]),
                created_at=session.started_at + timedelta(minutes=i*2)
            )
            
            if sender == 'bot':
                BotResponse.objects.create(
                    message=msg,
                    confidence_score=random.uniform(0.7, 0.99),
                    user_rating=random.choice([None, None, 4, 5]),
                    was_helpful=random.choice([None, True, True])
                )

    def seed_mood_entries(self):
        """Seed mood entries"""
        self.stdout.write('Seeding mood entries...')
        
        users = User.objects.filter(user_type__in=['student', 'adult'])
        count = 0
        
        for user in users[:40]:
            # Create entries for last 30 days
            for days_ago in range(random.randint(15, 30)):
                entry_date = date.today() - timedelta(days=days_ago)
                
                MoodEntry.objects.create(
                    user=user,
                    mood_level=random.choice(['very_bad', 'bad', 'neutral', 'good', 'very_good']),
                    mood_score=random.randint(1, 10),
                    emotions=['happy', 'content'] if random.random() > 0.5 else ['anxious', 'stressed'],
                    energy_level=random.randint(1, 10),
                    sleep_quality=random.randint(1, 10),
                    sleep_hours=random.uniform(4, 10),
                    activities=['study', 'exercise'] if random.random() > 0.5 else ['social', 'rest'],
                    triggers='Exam stress' if random.random() > 0.7 else '',
                    notes=random.choice(['Had a good day', 'Feeling better', 'Tough day', '']),
                    entry_date=entry_date
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} mood entries'))

    def seed_mood_patterns(self):
        """Seed mood patterns"""
        self.stdout.write('Seeding mood patterns...')
        
        users = User.objects.filter(mood_entries__isnull=False).distinct()
        count = 0
        
        for user in users[:20]:
            end = date.today()
            start = end - timedelta(days=30)
            
            MoodPattern.objects.create(
                user=user,
                start_date=start,
                end_date=end,
                period_type='monthly',
                average_mood_score=random.uniform(4, 8),
                mood_variance=random.uniform(0.5, 2.5),
                trend_direction=random.choice(['improving', 'stable', 'declining']),
                dominant_emotions=['anxious', 'stressed'],
                common_triggers=['academic_pressure', 'social_situations'],
                positive_activities=['exercise', 'music', 'friends'],
                recommendations='Consider daily mindfulness practice and regular sleep schedule',
                concern_level=random.randint(1, 5)
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} mood patterns'))

    def seed_crisis_alerts(self):
        """Seed crisis alerts"""
        self.stdout.write('Seeding crisis alerts...')
        
        users = User.objects.filter(user_type__in=['student', 'adult'])
        count = 0
        
        for _ in range(15):
            user = random.choice(users)
            detected_at = timezone.now() - timedelta(days=random.randint(0, 60))
            status = random.choice(['detected', 'acknowledged', 'contacted', 'resolved', 'escalated'])
            
            CrisisAlert.objects.create(
                user=user,
                severity=random.choice(['low', 'medium', 'high', 'critical']),
                status=status,
                crisis_type=random.choice(['suicidal_ideation', 'self_harm', 'severe_depression', 'panic_attack']),
                triggering_content='User expressed feelings of hopelessness',
                ai_confidence_score=random.uniform(0.7, 0.99),
                keywords_matched=['hopeless', 'give up', 'can\'t go on'],
                intervention_taken='Provided crisis resources and emergency contacts' if status != 'detected' else '',
                responder=User.objects.filter(user_type='moderator').first() if status != 'detected' else None,
                emergency_services_contacted=status == 'critical',
                emergency_contact_notified=status in ['contacted', 'resolved'],
                detected_at=detected_at,
                acknowledged_at=detected_at + timedelta(minutes=5) if status != 'detected' else None,
                resolved_at=detected_at + timedelta(hours=2) if status == 'resolved' else None
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} crisis alerts'))

    def seed_crisis_resources(self):
        """Seed crisis resources"""
        self.stdout.write('Seeding crisis resources...')
        
        resources = [
            {
                'country': 'Kenya',
                'name': 'Kenya Red Cross Counselling Hotline',
                'phone_number': '1199',
                'resource_type': 'hotline',
                'available_24_7': True
            },
            {
                'country': 'Kenya',
                'region': 'Nairobi',
                'name': 'Befrienders Kenya',
                'phone_number': '+254722178177',
                'resource_type': 'hotline',
                'available_24_7': True
            },
            {
                'country': 'USA',
                'name': '988 Suicide & Crisis Lifeline',
                'phone_number': '988',
                'resource_type': 'hotline',
                'available_24_7': True
            },
            {
                'country': 'UK',
                'name': 'Samaritans',
                'phone_number': '116123',
                'resource_type': 'hotline',
                'available_24_7': True
            },
            {
                'country': 'South Africa',
                'name': 'SADAG Mental Health Line',
                'phone_number': '0800567567',
                'resource_type': 'hotline',
                'available_24_7': True
            }
        ]
        
        count = 0
        for resource_data in resources:
            CrisisResource.objects.create(
                **resource_data,
                languages_supported=['English'],
                is_active=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} crisis resources'))

    def seed_forum_categories(self):
        """Seed forum categories"""
        self.stdout.write('Seeding forum categories...')
        
        categories = [
            {'name': 'Anxiety & Stress', 'slug': 'anxiety-stress', 'icon': '😰', 'color': '#FFA500'},
            {'name': 'Depression', 'slug': 'depression', 'icon': '😔', 'color': '#4169E1'},
            {'name': 'Academic Pressure', 'slug': 'academic-pressure', 'icon': '📚', 'color': '#32CD32'},
            {'name': 'Relationships', 'slug': 'relationships', 'icon': '❤️', 'color': '#FF69B4'},
            {'name': 'Self-Care', 'slug': 'self-care', 'icon': '🌸', 'color': '#9370DB'},
            {'name': 'Success Stories', 'slug': 'success-stories', 'icon': '🌟', 'color': '#FFD700'},
            {'name': 'General Support', 'slug': 'general-support', 'icon': '🤝', 'color': '#20B2AA'},
        ]
        
        count = 0
        for i, cat in enumerate(categories):
            ForumCategory.objects.create(
                **cat,
                description=f'Discussion space for {cat["name"].lower()} related topics',
                display_order=i,
                is_active=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} forum categories'))

    def seed_forum_posts(self):
        """Seed forum posts"""
        self.stdout.write('Seeding forum posts...')
        
        categories = list(ForumCategory.objects.all())
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        
        posts_data = [
            ('How do you deal with exam anxiety?', 'I get so nervous before exams that I can\'t sleep. Any tips?'),
            ('Feeling overwhelmed with coursework', 'Anyone else struggling to keep up with deadlines?'),
            ('Small wins today!', 'I managed to get out of bed and take a shower. Proud of myself!'),
            ('Looking for study buddies', 'Would love to connect with others for mutual support'),
            ('Mindfulness really helps', 'Started meditating and it\'s making a difference'),
            ('How to talk to parents about therapy?', 'I want to see a therapist but don\'t know how to ask'),
            ('Exercise and mental health', 'Running has been great for my mood'),
            ('Struggling with loneliness', 'New to campus and finding it hard to make friends'),
        ]
        
        count = 0
        for title, content in posts_data * 5:  # Create multiple posts
            author = random.choice(users)
            created = timezone.now() - timedelta(days=random.randint(0, 60))
            
            ForumPost.objects.create(
                category=random.choice(categories),
                author=author,
                title=title,
                content=content + ' ' + 'Would appreciate any advice or support from the community.',
                is_anonymous=random.choice([True, False, False]),
                view_count=random.randint(10, 500),
                like_count=random.randint(0, 50),
                reply_count=random.randint(0, 20),
                is_published=True,
                is_pinned=random.random() > 0.9,
                toxicity_score=random.uniform(0, 0.3),
                sentiment_score=random.uniform(-0.5, 0.8),
                created_at=created
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} forum posts'))

    def seed_forum_replies(self):
        """Seed forum replies"""
        self.stdout.write('Seeding forum replies...')
        
        posts = list(ForumPost.objects.all())
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        
        replies = [
            'Thank you for sharing. I can relate to this.',
            'Have you tried talking to a counselor? They really helped me.',
            'Sending you positive vibes! You\'ve got this!',
            'I struggled with this too. What helped me was...',
            'This is a safe space. We\'re here for you.',
            'Great question! Here\'s what worked for me...',
            'You\'re not alone in feeling this way.',
        ]
        
        count = 0
        for post in posts[:30]:
            for _ in range(random.randint(1, 8)):
                ForumReply.objects.create(
                    post=post,
                    author=random.choice(users),
                    content=random.choice(replies),
                    is_anonymous=random.choice([True, False, False]),
                    like_count=random.randint(0, 20),
                    is_published=True,
                    toxicity_score=random.uniform(0, 0.2),
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48))
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} forum replies'))

    def seed_forum_likes(self):
        """Seed forum likes"""
        self.stdout.write('Seeding forum likes...')
        
        posts = list(ForumPost.objects.all()[:50])
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        
        count = 0
        for post in posts:
            for _ in range(random.randint(0, 15)):
                try:
                    ForumLike.objects.create(
                        user=random.choice(users),
                        post=post
                    )
                    count += 1
                except:
                    pass  # Skip duplicates
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} forum likes'))

    def seed_forum_reports(self):
        """Seed forum reports"""
        self.stdout.write('Seeding forum reports...')
        
        posts = list(ForumPost.objects.all()[:10])
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        moderator = User.objects.filter(user_type='moderator').first()
        
        count = 0
        for post in posts[:5]:
            ForumReport.objects.create(
                reporter=random.choice(users),
                post=post,
                reason=random.choice(['spam', 'harassment', 'inappropriate', 'misinformation']),
                description='This content seems inappropriate for our community',
                status=random.choice(['pending', 'reviewed', 'resolved']),
                reviewed_by=moderator if random.random() > 0.5 else None,
                action_taken='Warned user' if random.random() > 0.5 else ''
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} forum reports'))

    def seed_counseling_appointments(self):
        """Seed counseling appointments"""
        self.stdout.write('Seeding counseling appointments...')
        
        clients = list(User.objects.filter(user_type__in=['student', 'adult']))
        therapists = list(TherapistProfile.objects.all())
        
        count = 0
        for client in clients[:25]:
            for _ in range(random.randint(1, 4)):
                therapist = random.choice(therapists)
                scheduled_date = date.today() + timedelta(days=random.randint(-30, 30))
                status = random.choice(['scheduled', 'confirmed', 'completed', 'completed', 'cancelled'])
                
                appointment = CounselingAppointment.objects.create(
                    client=client,
                    therapist=therapist,
                    session_type=random.choice(['video', 'audio', 'chat']),
                    scheduled_date=scheduled_date,
                    scheduled_time=time(random.randint(9, 16), random.choice([0, 30])),
                    duration_minutes=random.choice([45, 60]),
                    status=status,
                    meeting_link=f'https://meet.therapy.com/{random.randint(1000, 9999)}' if status != 'cancelled' else '',
                    fee=therapist.consultation_fee,
                    payment_status='paid' if status == 'completed' else 'pending',
                    attended=True if status == 'completed' else None,
                    next_session_recommended=random.choice([True, False]) if status == 'completed' else False
                )
                count += 1
                
                self.appointments = getattr(self, 'appointments', [])
                self.appointments.append(appointment)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} counseling appointments'))

    def seed_session_notes(self):
        """Seed session notes"""
        self.stdout.write('Seeding session notes...')
        
        completed_appointments = CounselingAppointment.objects.filter(status='completed')
        
        count = 0
        for appointment in completed_appointments[:20]:
            SessionNote.objects.create(
                appointment=appointment,
                therapist=appointment.therapist,
                presenting_issue='Client reported feelings of anxiety and stress related to academic pressure',
                observations='Client appeared engaged and willing to explore coping strategies',
                interventions_used='CBT techniques, breathing exercises, cognitive reframing',
                client_response='Positive response to interventions, willing to practice between sessions',
                homework_assigned='Practice daily breathing exercises, maintain mood journal',
                risk_assessment='Low risk, no immediate concerns',
                progress_notes='Client showing good progress, more aware of thought patterns',
                treatment_plan_updates='Continue with current approach, introduce mindfulness in next session',
                follow_up_needed=True,
                follow_up_date=appointment.scheduled_date + timedelta(days=14)
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} session notes'))

    def seed_therapist_reviews(self):
        """Seed therapist reviews"""
        self.stdout.write('Seeding therapist reviews...')
        
        completed_appointments = CounselingAppointment.objects.filter(
            status='completed',
            attended=True
        ).select_related('therapist', 'client')
        
        count = 0
        for appointment in completed_appointments[:30]:
            try:
                TherapistReview.objects.create(
                    appointment=appointment,
                    client=appointment.client,
                    therapist=appointment.therapist,
                    rating=random.randint(4, 5),
                    review_text=random.choice([
                        'Very helpful session. Dr. really listened and provided practical advice.',
                        'Excellent therapist. I feel much better after our sessions.',
                        'Professional and empathetic. Highly recommend.',
                        'Great experience. Looking forward to continuing therapy.',
                        'Compassionate and knowledgeable. Thank you!'
                    ]),
                    professionalism=random.randint(4, 5),
                    effectiveness=random.randint(4, 5),
                    empathy=random.randint(4, 5),
                    would_recommend=True,
                    is_anonymous=random.choice([True, False]),
                    is_published=True
                )
                count += 1
            except:
                pass  # Skip if review already exists
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} therapist reviews'))

    def seed_resources(self):
        """Seed mental health resources"""
        self.stdout.write('Seeding resources...')
        
        resources_data = [
            {
                'title': 'Understanding Anxiety: A Comprehensive Guide',
                'resource_type': 'article',
                'description': 'Learn about anxiety, its causes, and effective management strategies',
                'content': 'Anxiety is a natural response to stress...',
                'tags': ['anxiety', 'mental-health', 'coping'],
                'target_audience': ['students', 'adults'],
                'mental_health_topics': ['anxiety', 'stress-management']
            },
            {
                'title': '5-Minute Breathing Exercise',
                'resource_type': 'video',
                'description': 'Quick breathing exercise to reduce stress and anxiety',
                'video_url': 'https://youtube.com/watch?v=example',
                'duration_minutes': 5,
                'tags': ['breathing', 'relaxation', 'quick-relief'],
                'target_audience': ['everyone'],
                'mental_health_topics': ['anxiety', 'stress-management']
            },
            {
                'title': 'Guided Sleep Meditation',
                'resource_type': 'audio',
                'description': 'Relaxing meditation to help you fall asleep',
                'audio_url': 'https://audio.com/sleep-meditation',
                'duration_minutes': 20,
                'tags': ['sleep', 'meditation', 'relaxation'],
                'target_audience': ['everyone'],
                'mental_health_topics': ['sleep', 'relaxation']
            },
            {
                'title': 'CBT Thought Record Worksheet',
                'resource_type': 'worksheet',
                'description': 'Cognitive Behavioral Therapy worksheet for tracking and challenging negative thoughts',
                'file_url': 'https://resources.com/cbt-worksheet.pdf',
                'tags': ['cbt', 'worksheets', 'therapy'],
                'target_audience': ['students', 'adults'],
                'mental_health_topics': ['depression', 'anxiety', 'cbt']
            },
            {
                'title': 'Mindfulness for Beginners',
                'resource_type': 'article',
                'description': 'Introduction to mindfulness practice and its benefits',
                'content': 'Mindfulness is the practice of being present...',
                'duration_minutes': 10,
                'tags': ['mindfulness', 'meditation', 'beginner'],
                'target_audience': ['everyone'],
                'mental_health_topics': ['mindfulness', 'stress-management']
            },
            {
                'title': 'Dealing with Academic Stress',
                'resource_type': 'article',
                'description': 'Strategies for managing stress during exam periods',
                'content': 'Academic stress is common among students...',
                'tags': ['academic', 'stress', 'students'],
                'target_audience': ['students'],
                'mental_health_topics': ['stress-management', 'academic-pressure']
            }
        ]
        
        count = 0
        for resource_data in resources_data * 3:  # Create multiple copies
            Resource.objects.create(
                **resource_data,
                author=random.choice(['Dr. Smith', 'Mental Health Foundation', 'Wellness Center']),
                source='Mental Health Platform',
                difficulty_level=random.choice(['beginner', 'intermediate', 'advanced']),
                language='en',
                view_count=random.randint(50, 1000),
                like_count=random.randint(10, 200),
                share_count=random.randint(5, 50),
                average_rating=random.uniform(4.0, 5.0),
                is_featured=random.random() > 0.7,
                is_published=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} resources'))

    def seed_user_resource_interactions(self):
        """Seed user resource interactions"""
        self.stdout.write('Seeding user resource interactions...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        resources = list(Resource.objects.all())
        
        count = 0
        for user in users[:30]:
            for _ in range(random.randint(2, 8)):
                resource = random.choice(resources)
                try:
                    UserResourceInteraction.objects.create(
                        user=user,
                        resource=resource,
                        viewed=True,
                        completed=random.choice([True, False]),
                        liked=random.choice([True, False, False]),
                        saved=random.choice([True, False, False]),
                        rating=random.randint(3, 5) if random.random() > 0.5 else None,
                        was_helpful=random.choice([True, True, False, None]),
                        progress_percentage=random.randint(50, 100),
                        time_spent_minutes=random.randint(5, 30)
                    )
                    count += 1
                except:
                    pass  # Skip duplicates
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} resource interactions'))

    def seed_ai_recommendations(self):
        """Seed AI recommendations"""
        self.stdout.write('Seeding AI recommendations...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        resources = list(Resource.objects.all())
        therapists = list(TherapistProfile.objects.all())
        
        count = 0
        for user in users[:30]:
            for _ in range(random.randint(2, 5)):
                rec_type = random.choice(['resource', 'activity', 'therapist', 'coping_strategy'])
                
                recommendation = {
                    'user': user,
                    'recommendation_type': rec_type,
                    'title': f'Recommended: {random.choice(["Breathing Exercise", "Mindfulness Practice", "Therapist Consultation", "Self-Care Activity"])}',
                    'description': 'Based on your recent mood patterns, we recommend trying this resource',
                    'reason': 'Your mood logs indicate increased stress levels',
                    'confidence_score': random.uniform(0.7, 0.95),
                    'based_on_data': {'mood_average': 5.2, 'stress_level': 'high'},
                    'viewed': random.choice([True, False, False]),
                    'acted_upon': random.choice([True, False, False, False]),
                    'dismissed': False,
                    'priority': random.randint(1, 5)
                }
                
                if rec_type == 'resource':
                    recommendation['resource'] = random.choice(resources)
                elif rec_type == 'therapist':
                    recommendation['therapist'] = random.choice(therapists)
                
                AIRecommendation.objects.create(**recommendation)
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} AI recommendations'))

    def seed_wellness_activities(self):
        """Seed wellness activities"""
        self.stdout.write('Seeding wellness activities...')
        
        activities = [
            {
                'title': '4-7-8 Breathing Technique',
                'activity_type': 'breathing',
                'description': 'Calming breathing exercise to reduce anxiety',
                'instructions': '1. Breathe in for 4 seconds\n2. Hold for 7 seconds\n3. Exhale for 8 seconds\n4. Repeat 4 times',
                'duration_minutes': 5,
                'difficulty': 'easy',
                'benefits': ['reduces anxiety', 'improves sleep', 'calms nervous system'],
                'best_for': ['anxiety', 'sleep', 'stress']
            },
            {
                'title': 'Body Scan Meditation',
                'activity_type': 'meditation',
                'description': 'Mindful awareness of physical sensations',
                'instructions': 'Lie down comfortably and systematically focus on each part of your body',
                'duration_minutes': 15,
                'difficulty': 'medium',
                'benefits': ['relaxation', 'body awareness', 'stress relief'],
                'best_for': ['stress', 'anxiety', 'sleep']
            },
            {
                'title': 'Gratitude Journaling',
                'activity_type': 'journaling',
                'description': 'Daily practice of noting things you\'re grateful for',
                'instructions': 'Write down 3 things you\'re grateful for today',
                'duration_minutes': 10,
                'difficulty': 'easy',
                'benefits': ['positive thinking', 'improved mood', 'perspective'],
                'best_for': ['depression', 'negative thinking', 'self-esteem']
            },
            {
                'title': 'Progressive Muscle Relaxation',
                'activity_type': 'physical',
                'description': 'Systematic tension and release of muscle groups',
                'instructions': 'Tense each muscle group for 5 seconds, then release',
                'duration_minutes': 20,
                'difficulty': 'medium',
                'benefits': ['physical relaxation', 'stress relief', 'body awareness'],
                'best_for': ['stress', 'anxiety', 'tension']
            },
            {
                'title': '5-4-3-2-1 Grounding',
                'activity_type': 'grounding',
                'description': 'Grounding technique using your senses',
                'instructions': 'Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste',
                'duration_minutes': 5,
                'difficulty': 'easy',
                'benefits': ['grounding', 'anxiety relief', 'present moment'],
                'best_for': ['anxiety', 'panic', 'dissociation']
            },
            {
                'title': 'Morning Mindfulness',
                'activity_type': 'mindfulness',
                'description': 'Start your day with mindful awareness',
                'instructions': 'Spend 10 minutes in quiet reflection each morning',
                'duration_minutes': 10,
                'difficulty': 'easy',
                'benefits': ['mental clarity', 'stress reduction', 'focus'],
                'best_for': ['stress', 'focus', 'anxiety']
            }
        ]
        
        count = 0
        for activity_data in activities:
            WellnessActivity.objects.create(**activity_data, is_active=True)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} wellness activities'))

    def seed_user_activity_logs(self):
        """Seed user activity logs"""
        self.stdout.write('Seeding user activity logs...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        activities = list(WellnessActivity.objects.all())
        
        count = 0
        for user in users[:25]:
            for _ in range(random.randint(3, 10)):
                mood_before = random.randint(3, 7)
                mood_after = min(10, mood_before + random.randint(1, 3))
                
                UserActivityLog.objects.create(
                    user=user,
                    activity=random.choice(activities),
                    completed=True,
                    duration_minutes=random.randint(5, 30),
                    mood_before=mood_before,
                    mood_after=mood_after,
                    notes=random.choice(['Felt better after', 'Very helpful', 'Will do again', '']),
                    was_helpful=True if mood_after > mood_before else None,
                    completed_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} activity logs'))

    def seed_journal_entries(self):
        """Seed journal entries"""
        self.stdout.write('Seeding journal entries...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        
        prompts = [
            'What am I grateful for today?',
            'What challenged me today and how did I respond?',
            'What would make tomorrow better?',
            'How am I feeling right now?',
        ]
        
        entry_templates = [
            'Today was challenging but I managed to...',
            'I\'m feeling grateful for...',
            'Something that\'s been on my mind is...',
            'I noticed that I felt anxious when...',
            'A positive moment from today was...',
        ]
        
        count = 0
        for user in users[:20]:
            for _ in range(random.randint(5, 15)):
                JournalEntry.objects.create(
                    user=user,
                    title=random.choice(['Daily Reflection', 'My Thoughts', 'Today', 'Journal Entry', '']),
                    content=random.choice(entry_templates) + ' ' + 'And I realized that it\'s okay to feel this way. Tomorrow is a new day.',
                    prompt_used=random.choice(prompts) if random.random() > 0.5 else '',
                    sentiment_score=random.uniform(-0.3, 0.8),
                    emotions_detected={'primary': random.choice(['grateful', 'anxious', 'hopeful', 'sad'])},
                    themes=['self-reflection', 'growth'],
                    is_private=True,
                    mood_score=random.randint(4, 8),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 60))
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} journal entries'))

    def seed_notifications(self):
        """Seed notifications"""
        self.stdout.write('Seeding notifications...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        
        notifications_data = [
            {
                'notification_type': 'mood_check',
                'title': 'Time for your daily mood check-in',
                'message': 'How are you feeling today? Log your mood to track patterns.'
            },
            {
                'notification_type': 'appointment',
                'title': 'Upcoming therapy session',
                'message': 'You have a session scheduled for tomorrow at 2:00 PM'
            },
            {
                'notification_type': 'recommendation',
                'title': 'New resource recommended for you',
                'message': 'Based on your recent activity, we think this might help'
            },
            {
                'notification_type': 'achievement',
                'title': 'Achievement Unlocked! 🎉',
                'message': 'You\'ve logged your mood for 7 days in a row!'
            },
            {
                'notification_type': 'forum',
                'title': 'Someone replied to your post',
                'message': 'Check out the new responses in the forum'
            },
        ]
        
        count = 0
        for user in users[:30]:
            for _ in range(random.randint(3, 10)):
                notif = random.choice(notifications_data).copy()
                is_read = random.choice([True, False, False])
                
                Notification.objects.create(
                    user=user,
                    **notif,
                    is_read=is_read,
                    is_archived=False,
                    priority=random.randint(0, 3),
                    read_at=timezone.now() - timedelta(hours=random.randint(1, 48)) if is_read else None,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 14))
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} notifications'))

    def seed_achievements(self):
        """Seed achievements"""
        self.stdout.write('Seeding achievements...')
        
        achievements = [
            {'name': 'First Step', 'slug': 'first-step', 'icon': '👣', 'requirement_type': 'mood_entry', 'requirement_count': 1, 'points': 10},
            {'name': 'Week Warrior', 'slug': 'week-warrior', 'icon': '🔥', 'requirement_type': 'mood_streak', 'requirement_count': 7, 'points': 50},
            {'name': 'Mindful Master', 'slug': 'mindful-master', 'icon': '🧘', 'requirement_type': 'activities_completed', 'requirement_count': 10, 'points': 100},
            {'name': 'Journal Journey', 'slug': 'journal-journey', 'icon': '📔', 'requirement_type': 'journal_entries', 'requirement_count': 5, 'points': 30},
            {'name': 'Community Helper', 'slug': 'community-helper', 'icon': '🤝', 'requirement_type': 'forum_posts', 'requirement_count': 10, 'points': 40},
            {'name': 'Self-Care Champion', 'slug': 'self-care-champion', 'icon': '⭐', 'requirement_type': 'activities_completed', 'requirement_count': 25, 'points': 150},
            {'name': 'Month Milestone', 'slug': 'month-milestone', 'icon': '🏆', 'requirement_type': 'mood_streak', 'requirement_count': 30, 'points': 200},
        ]
        
        count = 0
        for achievement_data in achievements:
            Achievement.objects.create(**achievement_data, description=f'Earn this badge by completing {achievement_data["requirement_count"]} {achievement_data["requirement_type"]}', is_active=True)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} achievements'))

    def seed_user_achievements(self):
        """Seed user achievements"""
        self.stdout.write('Seeding user achievements...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        achievements = list(Achievement.objects.all())
        
        count = 0
        for user in users[:30]:
            for achievement in random.sample(achievements, random.randint(1, 4)):
                try:
                    UserAchievement.objects.create(
                        user=user,
                        achievement=achievement,
                        earned_at=timezone.now() - timedelta(days=random.randint(0, 60))
                    )
                    count += 1
                except:
                    pass  # Skip duplicates
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} user achievements'))

    def seed_user_streaks(self):
        """Seed user streaks"""
        self.stdout.write('Seeding user streaks...')
        
        users = list(User.objects.filter(user_type__in=['student', 'adult']))
        
        count = 0
        for user in users[:40]:
            UserStreak.objects.create(
                user=user,
                current_mood_streak=random.randint(0, 15),
                longest_mood_streak=random.randint(5, 30),
                current_activity_streak=random.randint(0, 10),
                longest_activity_streak=random.randint(3, 20),
                last_mood_entry=date.today() - timedelta(days=random.randint(0, 3)),
                last_activity=date.today() - timedelta(days=random.randint(0, 5)),
                total_points=random.randint(50, 500)
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} user streaks'))

    def seed_platform_analytics(self):
        """Seed platform analytics"""
        self.stdout.write('Seeding platform analytics...')
        
        count = 0
        for days_ago in range(30):
            analytics_date = date.today() - timedelta(days=days_ago)
            
            PlatformAnalytics.objects.create(
                date=analytics_date,
                total_users=100 + days_ago * 5,
                new_users=random.randint(5, 20),
                active_users=random.randint(50, 150),
                total_chat_sessions=random.randint(30, 100),
                total_messages=random.randint(200, 800),
                total_mood_entries=random.randint(50, 150),
                total_forum_posts=random.randint(10, 50),
                crisis_alerts=random.randint(0, 5),
                crisis_interventions=random.randint(0, 3),
                total_appointments=random.randint(10, 30),
                completed_appointments=random.randint(5, 25),
                users_by_country={'Kenya': 40, 'Uganda': 20, 'Tanzania': 15, 'Nigeria': 15, 'Others': 10},
                users_by_age_group={'18-24': 50, '25-34': 30, '35-44': 15, '45+': 5},
                average_mood_score=random.uniform(5.0, 7.5),
                average_sentiment=random.uniform(0.3, 0.7)
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} analytics records'))

    def seed_regional_trends(self):
        """Seed regional mental health trends"""
        self.stdout.write('Seeding regional trends...')
        
        regions = [
            ('Nairobi', 'Kenya'),
            ('Kampala', 'Uganda'),
            ('Dar es Salaam', 'Tanzania'),
            ('Lagos', 'Nigeria'),
            ('Cape Town', 'South Africa'),
        ]
        
        count = 0
        current_year = date.today().year
        
        for region, country in regions:
            for month in range(1, 7):  # Last 6 months
                RegionalMentalHealthTrend.objects.create(
                    region=region,
                    country=country,
                    year=current_year,
                    month=month,
                    total_users=random.randint(50, 200),
                    common_concerns=['anxiety', 'stress', 'depression'],
                    average_mood_score=random.uniform(5.0, 7.0),
                    crisis_rate=random.uniform(0.01, 0.05),
                    age_distribution={'18-24': 45, '25-34': 35, '35-44': 15, '45+': 5},
                    user_type_distribution={'student': 60, 'adult': 35, 'other': 5},
                    average_sessions_per_user=random.uniform(2.0, 5.0),
                    resource_usage={'articles': 40, 'videos': 30, 'activities': 30}
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} regional trends'))

    def seed_content_moderation_logs(self):
        """Seed content moderation logs"""
        self.stdout.write('Seeding content moderation logs...')
        
        moderator = User.objects.filter(user_type='moderator').first()
        posts = list(ForumPost.objects.all()[:10])
        
        count = 0
        for post in posts[:5]:
            ContentModerationLog.objects.create(
                moderator=moderator,
                forum_post=post,
                action_type=random.choice(['approve', 'flag', 'warn']),
                reason='AI flagged for review',
                notes='Reviewed and deemed appropriate',
                ai_suggested=True,
                ai_confidence=random.uniform(0.7, 0.95)
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} moderation logs'))

    def seed_system_configuration(self):
        """Seed system configuration"""
        self.stdout.write('Seeding system configuration...')
        
        admin = User.objects.filter(is_superuser=True).first()
        
        configs = [
            {'key': 'crisis_keywords', 'value': ['suicide', 'kill myself', 'end it all', 'hopeless'], 'description': 'Keywords that trigger crisis detection'},
            {'key': 'mood_reminder_time', 'value': '20:00', 'description': 'Daily mood check-in reminder time'},
            {'key': 'min_therapist_rating', 'value': 3.5, 'description': 'Minimum rating for therapist visibility'},
            {'key': 'forum_moderation_threshold', 'value': 0.7, 'description': 'AI confidence threshold for auto-flagging'},
            {'key': 'max_chat_session_duration', 'value': 120, 'description': 'Maximum chat session duration in minutes'},
        ]
        
        count = 0
        for config in configs:
            SystemConfiguration.objects.create(**config, is_active=True, updated_by=admin)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} system configurations'))

    def seed_audit_logs(self):
        """Seed audit logs"""
        self.stdout.write('Seeding audit logs...')
        
        users = list(User.objects.filter(is_staff=True))
        
        actions = [
            ('create', 'User', 'Created new user account'),
            ('update', 'TherapistProfile', 'Updated therapist credentials'),
            ('delete', 'ForumPost', 'Removed inappropriate content'),
            ('approve', 'CounselingAppointment', 'Approved therapy appointment'),
            ('verify', 'TherapistProfile', 'Verified therapist credentials'),
        ]
        
        count = 0
        for _ in range(50):
            action, model_name, description = random.choice(actions)
            
            AuditLog.objects.create(
                user=random.choice(users),
                action=action,
                model_name=model_name,
                object_id=str(random.randint(1, 100)),
                changes={
                    'action': description,
                    'timestamp': timezone.now().isoformat(),
                    'field_changed': 'status' if action == 'update' else None
                },
                ip_address=f'192.168.1.{random.randint(1, 255)}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} audit logs'))