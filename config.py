# config.py
import os

# Application Configuration
APP_CONFIG = {
    'APP_NAME': 'WSM Management System',
    'VERSION': '1.0.0',
    'DEFAULT_TEMPLATE': 'STD_WSM',
    'STATUS_OPTIONS': [
        'Submitted',
        'Approved', 
        'Waiting for MRO Confirmation',
        'Rejected',
        'Completed'
    ]
}

# Database Configuration
DB_CONFIG = {
    'DATABASE_NAME': 'wsm_projects.db',
    'INITIAL_USER': {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@company.com'
    }
}

# PDF Configuration
PDF_CONFIG = {
    'DEFAULT_ORIENTATION': 'portrait',
    'PAGE_SIZE': 'A4',
    'MARGINS': '0.5in'
}