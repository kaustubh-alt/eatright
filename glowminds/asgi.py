import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glowminds.settings')

# Setup Django before importing anything Django-related
django.setup()

# Now import your routing AFTER setup
from eatright.routing import websocket_urlpatterns

# Application definition
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
