from pathlib import Path
import os
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.environ.get('STUDIO_SECRET_KEY','development-only-change-before-deployment')
DEBUG=os.environ.get('STUDIO_DEBUG','1')=='1'
ALLOWED_HOSTS=os.environ.get('STUDIO_ALLOWED_HOSTS','127.0.0.1,localhost').split(',')
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','studio']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'studio.sqlite3'}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-gb';TIME_ZONE='Africa/Accra';USE_TZ=True
STATIC_URL='static/';DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login';LOGIN_REDIRECT_URL='projects';LOGOUT_REDIRECT_URL='home'
EMAIL_BACKEND=os.environ.get('STUDIO_EMAIL_BACKEND','django.core.mail.backends.console.EmailBackend')
EMAIL_HOST=os.environ.get('STUDIO_EMAIL_HOST','');EMAIL_PORT=int(os.environ.get('STUDIO_EMAIL_PORT','587'))
EMAIL_HOST_USER=os.environ.get('STUDIO_EMAIL_USER','');EMAIL_HOST_PASSWORD=os.environ.get('STUDIO_EMAIL_PASSWORD','')
EMAIL_USE_TLS=os.environ.get('STUDIO_EMAIL_TLS','1')=='1'
DEFAULT_FROM_EMAIL=os.environ.get('STUDIO_FROM_EMAIL','BuildAI <no-reply@example.invalid>')
PRIVATE_STORAGE=BASE_DIR/'private_uploads'
SESSION_COOKIE_HTTPONLY=True;SESSION_COOKIE_SAMESITE='Lax';CSRF_COOKIE_SAMESITE='Lax';SESSION_COOKIE_AGE=86400
SECURE_CONTENT_TYPE_NOSNIFF=True;SECURE_REFERRER_POLICY='strict-origin-when-cross-origin';X_FRAME_OPTIONS='DENY'
if not DEBUG:
 if SECRET_KEY=='development-only-change-before-deployment':raise RuntimeError('Set STUDIO_SECRET_KEY before deployment')
 SESSION_COOKIE_SECURE=True;CSRF_COOKIE_SECURE=True;SECURE_SSL_REDIRECT=True
 SECURE_HSTS_SECONDS=31536000;SECURE_HSTS_INCLUDE_SUBDOMAINS=True
