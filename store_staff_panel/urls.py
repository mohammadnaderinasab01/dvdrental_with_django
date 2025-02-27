from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('payments', views.StaffPaymentView)

urlpatterns = [
    path('return-rental/<int:pk>/', views.ReturnRentalView.as_view(), name="return_rental"),
    path('rent-film/', views.RentFilmView.as_view(), name="rent_film"),
    path('', include(router.urls)),
    path('total-revenue/', views.TotalRevenueView.as_view(), name='total_revenue'),
    path('add-film-inventory/<int:pk>/', views.AddFilmInventoryToStoreView.as_view(), name="add_film"),
]
