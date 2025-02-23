from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('customers', views.CustomerViewSet)
router.register('staffs', views.StaffViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('top-renting-customers/', views.TopRentingCustomersView.as_view()),
    path('store-total-revenue/<int:pk>/', views.StoreTotalRevenueView.as_view()),
    path('top-performing-stores/', views.TopPerformingStoresView.as_view()),
]
