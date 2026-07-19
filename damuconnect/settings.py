from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = [
    'mysql-damuconnect.alwaysdata.net',
    '127.0.0.1',
    'localhost',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'corsheaders',
    'axes',              # brute force login protection
    # local apps
    'accounts',
    'entities',
    'donors',
    'donations',
    'inventory',
    'dashboard',
    'notifications',
    'chatbot',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',   # must be last
]

ROOT_URLCONF = 'damuconnect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'damuconnect.wsgi.application'

# Database credentials from .env
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'damuconnect_db',
            'USER': 'damuconnect',
            'PASSWORD': 'modcom2026',
            'HOST': 'mysql-damuconnect.alwaysdata.net',
            'OPTIONS': {
                'sql_mode': 'STRICT_TRANS_TABLES',
            }
        }
    }
# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# django-axes — brute force protection
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',          # axes must be first
    'django.contrib.auth.backends.ModelBackend',    # default Django auth
]

# Lock account after 5 failed login attempts
AXES_FAILURE_LIMIT = 5
# Lock for 30 minutes
AXES_COOLOFF_TIME = timedelta(minutes=30)
# Lock by IP address
AXES_LOCKOUT_PARAMETERS = ['ip_address']
# Return clean error message
AXES_LOCKOUT_CALLABLE = 'accounts.utils.axes_lockout_response'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'accounts.utils.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    # Rate limiting — max 100 requests per minute per user
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',   # unauthenticated users
        'rest_framework.throttling.UserRateThrottle',   # authenticated users
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',    # unauthenticated — 20 requests per minute
        'user': '100/minute',   # authenticated — 100 requests per minute
        'login': '5/minute',    # login endpoint — 5 attempts per minute
    },
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    # Add user role and id into the token payload
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
}

# CORS — only allow listed origins
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
# Only allow safe methods from unknown origins
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# Security headers — protect against common web attacks
SECURE_BROWSER_XSS_FILTER = True                   # block XSS attacks
SECURE_CONTENT_TYPE_NOSNIFF = True                 # block MIME sniffing
X_FRAME_OPTIONS = 'DENY'                           # block clickjacking
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

GROQ_API_KEY = env('GROQ_API_KEY', default='')

# Swagger docs
SPECTACULAR_SETTINGS = {
    'TITLE': 'DamuConnect API',
    'DESCRIPTION': 'Blood Donation Management System API',
    'VERSION': '1.0.0',
    # Require JWT token in Swagger UI
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}

# Logging — records all activity to a file
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'damuconnect.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    # Log all failed login attempts
    'loggers': {
        'axes': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
