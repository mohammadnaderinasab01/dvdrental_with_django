from rest_framework.permissions import BasePermission
from store.models import Staff
from payment.models import Rental
from films.models import Inventory


class HasStoreStaffAccessRental(BasePermission):
    def has_permission(self, request, view):
        try:
            staff = Staff.objects.get(user__id=request.user.id)
            rental = Rental.objects.get(rental_id=view.kwargs.get('pk'))
            return request.user and request.user.is_authenticated and request.user.is_store_staff and staff.staff_id == rental.staff.staff_id
        except:
            return False


class IsStoreStaff(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user and request.user.is_authenticated and request.user.is_store_staff
        except:
            return False
