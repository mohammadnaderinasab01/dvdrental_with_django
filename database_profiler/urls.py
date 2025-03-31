from django.urls import path, include
from . import views

urlpatterns = [
    path('queries/', views.QueriesView.as_view(), name='database_profiler__queries')
]
