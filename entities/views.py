from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin, IsEntity
from accounts.models import User
from accounts.utils import api_response
from .models import Entity
from .serializers import EntitySerializer, EntityRegisterSerializer, EntityApprovalSerializer, EntityUpdateSerializer
from notifications.utils import send_notification


class EntityProfileView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsEntity()]

    def get(self, request):
        entity = request.user.entity_profile
        return api_response("success", "Profile retrieved.", EntitySerializer(entity).data)

    def post(self, request):
        if request.user.role != 'entity':
            return api_response("error", "Only entity users can create an entity profile.", None, 403)
        if hasattr(request.user, 'entity_profile'):
            return api_response("error", "Entity profile already exists.", None, 400)
        serializer = EntityRegisterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        entity = serializer.save()
        return api_response("success", "Entity profile created.", EntitySerializer(entity).data, 201)

    def patch(self, request):
        # Entity updates their own profile
        entity = request.user.entity_profile
        serializer = EntityUpdateSerializer(entity, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        serializer.save()
        return api_response("success", "Profile updated.", EntitySerializer(entity).data)


class AdminEntityListView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        status = request.query_params.get('status')
        entities = Entity.objects.all()
        if status:
            entities = entities.filter(status=status)
        return api_response("success", "Entities retrieved.", EntitySerializer(entities, many=True).data)


class AdminEntityApprovalView(APIView):
    permission_classes = (IsAdmin,)

    def patch(self, request, pk):
        try:
            entity = Entity.objects.get(pk=pk)
        except Entity.DoesNotExist:
            return api_response("error", "Entity not found.", None, 404)
        serializer = EntityApprovalSerializer(entity, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        entity = serializer.save(registered_by=request.user)
        # Notify the entity user about approval/rejection
        send_notification(
            entity.user,
            f"Entity {entity.status.capitalize()}",
            f"Your entity '{entity.entity_name}' has been {entity.status} by admin."
        )
        return api_response("success", f"Entity {entity.status}.", EntitySerializer(entity).data)


class AdminDeactivateUserView(APIView):
    permission_classes = (IsAdmin,)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return api_response("error", "User not found.", None, 404)
        user.is_active = not user.is_active
        user.save()
        status_msg = "activated" if user.is_active else "deactivated"
        return api_response("success", f"User {status_msg}.", None)
