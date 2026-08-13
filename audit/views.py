from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin
from accounts.utils import api_response
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        logs = AuditLog.objects.select_related('user').all()

        model_name = request.query_params.get('model_name')
        if model_name:
            logs = logs.filter(model_name=model_name)

        action = request.query_params.get('action')
        if action:
            logs = logs.filter(action=action)

        user_id = request.query_params.get('user_id')
        if user_id:
            logs = logs.filter(user_id=user_id)

        return api_response("success", "Audit logs retrieved.", AuditLogSerializer(logs, many=True).data)
