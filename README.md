# 🧠 Global AI-Powered Mental Health Support Platform

A comprehensive, scalable mental health support platform leveraging AI to provide accessible mental health resources, crisis intervention, professional counseling, and community support to users worldwide.

## 🌟 Features

### Core Functionality
- **AI Therapy Chatbot**: 24/7 conversational support using advanced NLP and therapeutic frameworks (CBT, DBT)
- **Crisis Detection & Intervention**: Real-time AI-powered crisis detection with immediate intervention protocols
- **Mood Tracking & Analytics**: Daily mood logging with AI-driven pattern analysis and insights
- **Professional Counseling**: Connect with verified therapists for video, audio, or text sessions
- **Community Forum**: Safe, moderated peer support community
- **Resource Library**: Curated mental health articles, videos, exercises, and worksheets
- **Wellness Activities**: Guided meditation, breathing exercises, journaling prompts
- **Multilingual Support**: Available in 8+ languages

### Advanced Features
- **Personalized AI Recommendations**: Context-aware suggestions for resources, activities, and therapists
- **Gamification**: Achievement system, streaks, and points to encourage engagement
- **Emergency Contact Management**: Quick access to crisis hotlines and personal emergency contacts
- **Privacy-First Design**: Anonymous posting options, HIPAA-compliant data handling
- **Regional Mental Health Trends**: Anonymized analytics for research and policy-making

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 14+
- **Caching**: Redis
- **Task Queue**: Celery with Redis broker
- **WebSocket**: Django Channels for real-time chat
- **AI/ML**: OpenAI GPT-4, Custom NLP models, Sentiment analysis
- **Storage**: AWS S3 (configurable)
- **Video Conferencing**: Zoom API integration
- **Payment**: Stripe
- **Monitoring**: Sentry

### System Requirements
- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Node.js 16+ (for frontend)
- 4GB RAM minimum (8GB recommended)
- 20GB storage minimum

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/mental-health-platform.git
cd mental-health-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=mental_health_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Services
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# AWS S3 (Optional)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Crisis Alerts
CRISIS_ALERT_EMAIL=crisis@yourplatform.com
ENABLE_EMERGENCY_SERVICES=True

# Twilio (SMS)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Stripe (Payments)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=

# Zoom (Video Sessions)
ZOOM_API_KEY=
ZOOM_API_SECRET=
```

### 5. Database Setup
```bash
# Create database
createdb mental_health_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata initial_data.json
```

### 6. Start Services

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker -l info
```

**Terminal 3 - Celery Beat (Scheduled Tasks):**
```bash
celery -A config beat -l info
```

**Terminal 4 - Channels (WebSocket):**
```bash
daphne -b 0.0.0.0 -p 8001 config.asgi:application
```

### 7. Access the Platform
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs/
- **Frontend**: http://localhost:3000 (if running separately)

## 📁 Project Structure

```
mental-health-platform/
├── apps/
│   ├── users/              # User management
│   ├── chat/               # AI chatbot
│   ├── mood/               # Mood tracking
│   ├── crisis/             # Crisis detection & intervention
│   ├── forum/              # Community forum
│   ├── counseling/         # Professional therapy sessions
│   ├── resources/          # Mental health resources
│   ├── activities/         # Wellness activities
│   ├── notifications/      # User notifications
│   ├── gamification/       # Achievements & streaks
│   ├── analytics/          # Platform analytics
│   └── moderation/         # Content moderation
├── config/
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL configuration
│   ├── asgi.py             # ASGI config (WebSocket)
│   └── wsgi.py             # WSGI config
├── ml_models/              # ML model files
├── static/                 # Static files
├── media/                  # User uploads
├── templates/              # HTML templates
├── locale/                 # Translation files
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── manage.py               # Django management
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker compose
└── README.md               # This file
```

## 🔐 Security & Compliance

### HIPAA Compliance
- **Data Encryption**: AES-256 encryption at rest and in transit
- **Audit Logging**: Comprehensive audit trail for all data access
- **Access Controls**: Role-based access control (RBAC)
- **Data Retention**: Configurable retention policies
- **Session Management**: Auto-logout after inactivity

### Security Best Practices
- JWT-based authentication
- Rate limiting on all endpoints
- SQL injection prevention
- XSS protection
- CSRF protection
- Regular security audits

## 🌍 Internationalization

Supported languages:
- English (en)
- Spanish (es)
- French (fr)
- Arabic (ar)
- Chinese (zh)
- Hindi (hi)
- Swahili (sw)
- Portuguese (pt)

Add new translations:
```bash
python manage.py makemessages -l es
python manage.py compilemessages
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.chat

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📊 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`

### Key Endpoints

**Authentication:**
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token

**Chat:**
- `POST /api/chat/sessions/` - Start new chat session
- `POST /api/chat/messages/` - Send message
- `GET /api/chat/sessions/{id}/` - Get session history

**Mood Tracking:**
- `POST /api/mood/entries/` - Log mood entry
- `GET /api/mood/patterns/` - Get mood patterns
- `GET /api/mood/insights/` - Get AI insights

**Crisis:**
- `POST /api/crisis/alert/` - Trigger crisis alert
- `GET /api/crisis/resources/` - Get crisis resources

**Forum:**
- `GET /api/forum/posts/` - List forum posts
- `POST /api/forum/posts/` - Create post
- `POST /api/forum/posts/{id}/replies/` - Reply to post

**Counseling:**
- `GET /api/counseling/therapists/` - List therapists
- `POST /api/counseling/appointments/` - Book appointment
- `GET /api/counseling/appointments/` - List appointments

## 🤖 AI Configuration

### Crisis Detection
The platform uses a multi-layered approach:
1. Keyword detection (immediate)
2. Sentiment analysis (contextual)
3. ML model prediction (behavioral patterns)
4. Risk scoring (0-10 scale)

### Chatbot Configuration
- **Framework**: Cognitive Behavioral Therapy (CBT) by default
- **Temperature**: 0.7 (configurable)
- **Max Tokens**: 500 per response
- **Context Window**: Last 10 messages

## 📈 Monitoring & Analytics

### Application Monitoring
- **Sentry**: Error tracking and performance monitoring
- **Celery Flower**: Task queue monitoring
- **Django Debug Toolbar**: Development debugging

### Business Analytics
- User engagement metrics
- Crisis intervention statistics
- Therapist performance
- Regional mental health trends
- Resource effectiveness

## 🐳 Docker Deployment

```bash
# Build and start containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

## 🚢 Production Deployment

### Prerequisites
- Ubuntu 20.04+ or similar
- Nginx
- Supervisor (for process management)
- PostgreSQL
- Redis

### Deployment Steps
1. Clone repository on server
2. Configure environment variables
3. Install dependencies
4. Run migrations
5. Collect static files: `python manage.py collectstatic`
6. Configure Nginx as reverse proxy
7. Set up SSL certificate (Let's Encrypt)
8. Configure Supervisor for Gunicorn, Celery, and Channels
9. Enable monitoring and logging

### Scaling Considerations
- Use load balancer for multiple application servers
- Database replication for read scaling
- Redis Cluster for caching
- CDN for static/media files
- Separate Celery workers for different task types

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation
- Add type hints where applicable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Resources

### Crisis Resources
If you or someone you know is in crisis:
- **National Suicide Prevention Lifeline (US)**: 1-800-273-8255
- **Crisis Text Line**: Text HOME to 741741
- **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

### Documentation
- [User Guide](docs/user-guide.md)
- [Therapist Guide](docs/therapist-guide.md)
- [API Reference](docs/api-reference.md)
- [Development Guide](docs/development.md)

### Contact
- **Email**: support@mentalhealthplatform.com
- **Website**: https://mentalhealthplatform.com
- **GitHub Issues**: https://github.com/your-org/mental-health-platform/issues

## 🙏 Acknowledgments

- Mental health professionals who provided guidance
- Open-source community
- All contributors and supporters

## ⚠️ Disclaimer

This platform is designed to provide support and resources but is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified health providers with questions regarding medical conditions. If you are experiencing a mental health crisis, please contact emergency services or a crisis hotline immediately.

---

**Made with ❤️ for global mental health wellness