from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.utils import api_response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        notifications = request.user.notifications.all()
        unread = request.query_params.get('unread')
        if unread and unread.lower() == 'true':
            notifications = notifications.filter(is_read=False)
        return api_response("success", "Notifications retrieved.", NotificationSerializer(notifications, many=True).data)


class NotificationUnreadCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        count = request.user.notifications.filter(is_read=False).count()
        return api_response("success", "Unread count retrieved.", {"unread_count": count})


class NotificationMarkReadView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk):
        try:
            notification = request.user.notifications.get(pk=pk)
        except Notification.DoesNotExist:
            return api_response("error", "Notification not found.", None, 404)
        notification.is_read = True
        notification.save()
        return api_response("success", "Notification marked as read.", NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return api_response("success", "All notifications marked as read.", None)


class NotificationDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            notification = request.user.notifications.get(pk=pk)
        except Notification.DoesNotExist:
            return api_response("error", "Notification not found.", None, 404)
        notification.delete()
        return api_response("success", "Notification deleted.", None)
