from django.contrib import admin
from .models import SiteConfig


@admin.register(SiteConfig)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')  # Display key, truncated value, and description
    search_fields = ('key', 'description')  # Allow searching by key or description
    list_filter = ('key',)  # Optional: Add filters if needed

    def save_model(self, request, obj, form, change):
        """ Invalidate cache after saving to ensure the latest value is used """
        super().save_model(request, obj, form, change)
        cache_key = obj.key
        from django.core.cache import cache
        cache.delete(cache_key)  # Remove cached value to refresh
