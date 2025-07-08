import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import Book
from asgiref.sync import sync_to_async


@sync_to_async
def get_book_available_copies(book_id):
    try:
        book = Book.objects.get(id=book_id)
        return book.available_copies
    except Book.DoesNotExist:
        return


class BookAvailabilityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.book_id = self.scope['url_route']['kwargs']['book_id']
        self.group_name = f'book_availability_{self.book_id}'

        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            await self.close()
            return

        # Join book availability group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        available_copies = await get_book_available_copies(self.book_id)

        await self.send(text_data=json.dumps({
            "type": "book_available",
            "book_id": self.book_id,
            "available_copies": available_copies
        }))


    async def disconnect(self, close_code):
        # Leave book availability group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )



    async def book_available(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'book_available',
            'book_id': event['book_id'],
            'available_copies': event['available_copies']
        }))

