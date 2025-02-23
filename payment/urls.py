from django.urls import path
from . import views


urlpatterns = [
    path('rentals/', views.RentalListView.as_view(), name='rentals'),
    path('rentals/<int:pk>/', views.RentalDetailsView.as_view(), name="rental_details"),
]
