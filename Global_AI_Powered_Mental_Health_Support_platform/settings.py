import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-zpq2vzs+=d=90s@w&#ro%pf9yi8aw+&jalpqgv)fxa+aok5%8y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web_application',
]
# Custom User Model
AUTH_USER_MODEL = 'web_application.User'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Global_AI_Powered_Mental_Health_Support_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Global_AI_Powered_Mental_Health_Support_platform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported Languages
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('ar', 'Arabic'),
    ('zh', 'Chinese'),
    ('hi', 'Hindi'),
    ('sw', 'Swahili'),
    ('pt', 'Portuguese'),
]


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI Services Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')
OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.7'))

# Alternative AI providers
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')

# Natural Language Processing
NLP_MODEL_PATH = BASE_DIR / 'ml_models' / 'sentiment_analysis'
CRISIS_DETECTION_MODEL_PATH = BASE_DIR / 'ml_models' / 'crisis_detection'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@mentalhealthplatform.com')

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Video Conferencing (for therapy sessions)
ZOOM_API_KEY = os.environ.get('ZOOM_API_KEY')
ZOOM_API_SECRET = os.environ.get('ZOOM_API_SECRET')

# Payment Processing (Stripe)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Crisis Alert Settings
CRISIS_ALERT_EMAIL = os.environ.get('CRISIS_ALERT_EMAIL', 'crisis@mentalhealthplatform.com')
CRISIS_ALERT_PHONE = os.environ.get('CRISIS_ALERT_PHONE')
ENABLE_EMERGENCY_SERVICES_NOTIFICATION = os.environ.get('ENABLE_EMERGENCY_SERVICES', 'True') == 'True'

# Content Moderation
ENABLE_AI_MODERATION = os.environ.get('ENABLE_AI_MODERATION', 'True') == 'True'
TOXICITY_THRESHOLD = float(os.environ.get('TOXICITY_THRESHOLD', '0.7'))
AUTO_FLAG_THRESHOLD = float(os.environ.get('AUTO_FLAG_THRESHOLD', '0.85'))

# Analytics & Monitoring
ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'True') == 'True'

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# HIPAA Compliance Settings
DATA_ENCRYPTION_ENABLED = os.environ.get('DATA_ENCRYPTION_ENABLED', 'True') == 'True'
AUDIT_LOG_RETENTION_DAYS = int(os.environ.get('AUDIT_LOG_RETENTION_DAYS', '2555'))  # 7 years
AUTO_LOGOUT_TIME = int(os.environ.get('AUTO_LOGOUT_TIME', '900'))  # 15 minutes

# Platform-specific Settings
MINIMUM_AGE = int(os.environ.get('MINIMUM_AGE', '13'))
REQUIRES_PARENTAL_CONSENT_AGE = int(os.environ.get('PARENTAL_CONSENT_AGE', '18'))

# AI Chat Settings
MAX_CHAT_SESSION_DURATION = int(os.environ.get('MAX_CHAT_SESSION_DURATION', '3600'))  # 1 hour
MAX_MESSAGES_PER_SESSION = int(os.environ.get('MAX_MESSAGES_PER_SESSION', '100'))
AI_RESPONSE_TIMEOUT = int(os.environ.get('AI_RESPONSE_TIMEOUT', '30'))  # seconds

# Mood Tracking
MOOD_REMINDER_TIME = os.environ.get('MOOD_REMINDER_TIME', '20:00')  # 8 PM
MOOD_STREAK_THRESHOLD = int(os.environ.get('MOOD_STREAK_THRESHOLD', '7'))  # days

# Gamification
ENABLE_GAMIFICATION = os.environ.get('ENABLE_GAMIFICATION', 'True') == 'True'
POINTS_PER_MOOD_ENTRY = int(os.environ.get('POINTS_PER_MOOD_ENTRY', '10'))
POINTS_PER_CHAT_SESSION = int(os.environ.get('POINTS_PER_CHAT_SESSION', '20'))
POINTS_PER_ACTIVITY_COMPLETION = int(os.environ.get('POINTS_PER_ACTIVITY_COMPLETION', '15'))

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
