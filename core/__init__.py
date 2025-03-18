# dvdrental_project/__init__.py
from .celery import app as celery_app
from pymongo_wrapper.connection import connect

__all__ = ('celery_app',)


# Initialize the connection once at startup
mongo_dvdrental_db = connect("dvdrental_django_project_test", "mongodb://127.0.0.1:27017")
