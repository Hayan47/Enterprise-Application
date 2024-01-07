import os

os.environ.setdefault('DB_ENGINE', 'postgresql') # change database sqlite3 / postgresql
DATABASE_ENGINE = os.environ.get('DB_ENGINE')

if DATABASE_ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        },
    }
elif DATABASE_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mydatabase',
            'USER': 'postgres',
            'PASSWORD': 'admin',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
else:
    raise ValueError(f"Invalid database engine: {DATABASE_ENGINE}")

os.environ.setdefault('MAX_UPLOAD_FILES', '3') #change it to what you need
MAX_UPLOAD_FILES = int(os.environ.get('MAX_UPLOAD_FILES'))