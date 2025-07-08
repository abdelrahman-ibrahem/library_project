"""
ASGI config for library project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Set the default Django settings module before importing anything that needs Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')

django.setup()

from library.middleware import TokenAuthMiddlewareStack
from apps.library_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )
})