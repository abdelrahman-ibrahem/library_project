from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/books/availability/<int:book_id>/', consumers.BookAvailabilityConsumer.as_asgi()),
]
