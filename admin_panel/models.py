from django.db import models
from django.core.cache import cache


class SiteConfigManager(models.Manager):
    def get_config(self, key, default=None):
        cached_key = key
        cached_value = cache.get(cached_key)
        if cached_value is not None:
            return cached_value

        try:
            config = self.get(key=key)
            value = config.value
            cache.set(cached_key, value, 3600)  # Cache for 1 hour
            return value
        except self.model.DoesNotExist:
            return default


class SiteConfig(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    objects = SiteConfigManager()
