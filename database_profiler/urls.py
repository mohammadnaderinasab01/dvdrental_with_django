from django.urls import path, include
from . import views

urlpatterns = [
    path('queries/', views.QueriesView.as_view(), name='database_profiler__queries'),
    path('slow-queries/', views.SlowQueriesView.as_view(), name='database_profiler__slow_queries'),
    path('most-slow-queries/', views.MostSlowQueriesView.as_view(), name='database_profiler__most_slow_queries'),
    path('most-used-endpoints/', views.MostUsedEndpointsView.as_view(), name='database_profiler__most_used_endpoints'),
    path('most-used-tables/', views.MostUsedTablesView.as_view(), name='database_profiler__most_used_tables'),
]
