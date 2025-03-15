from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def check_polygon_intersection(polygon_id):
    # Логика проверки пересечения полигонов
    ...

    # Отправка уведомления через WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',
        {
            'type': 'send_notification',
            'message': 'Полигоны пересекаются.'
        }
    )