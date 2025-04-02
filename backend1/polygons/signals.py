from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Polygon
from django.core.cache import cache


@receiver(post_save, sender=Polygon)
@receiver(post_delete, sender=Polygon)
def update_polygon_cache(sender, **kwargs):
    cache.delete("polygons")
