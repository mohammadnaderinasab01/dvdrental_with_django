from typing import Any
from django.contrib.auth.models import AbstractUser, UserManager as AbstractUserManager, \
    Group, Permission, User
from django.utils.translation import gettext_lazy as _
from django.db import models
from utils.validators import only_int
import uuid


class UserManager(AbstractUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The email must be set"))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    email = models.EmailField(max_length=255, unique=True, primary_key=False)
    password = models.CharField(max_length=255)

    is_customer = models.BooleanField(default=False)
    is_store_staff = models.BooleanField(default=False)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return str(self.email)


# Step 1: Create a Proxy Model for the Group
class CustomGroup(Group):
    class Meta:
        proxy = True

    def remove_all_permissions(self):
        self.permissions.clear()
        self.save()

    def remove_staff_permissions():
        try:
            staff_group = CustomGroup.objects.get(name='staff')
            staff_group.remove_all_permissions()
            print("All permissions removed from the staff group.")
        except CustomGroup.DoesNotExist:
            print("Staff group does not exist.")
