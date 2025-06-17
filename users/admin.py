from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    ordering = ('email',)  # Replace 'username' with 'email'
    list_display = [
        field.name for field in User._meta.fields if field.name != "password"
    ]  # Show all fields except 'password'

    # Define fieldsets for the "Change User" page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    # Define add_fieldsets for the "Add User" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),  # Use password1 and password2
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Hash password only for new users
            obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)


# Register the custom admin class
admin.site.register(User, CustomUserAdmin)
