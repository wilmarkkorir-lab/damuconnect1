from django.urls import path
from .views import GeneralChatView, SmartChatView

urlpatterns = [
    path('general/', GeneralChatView.as_view(), name='chat-general'),  # POST — no token needed
    path('smart/', SmartChatView.as_view(), name='chat-smart'),        # POST — token required
]
