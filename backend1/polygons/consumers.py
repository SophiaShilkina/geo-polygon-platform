import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PolygonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("polygon_notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("polygon_notifications", self.channel_name)

    async def polygon_intersection(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "intersections": event["intersections"]
        }))
