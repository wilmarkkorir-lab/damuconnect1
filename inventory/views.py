from rest_framework.views import APIView
from accounts.permissions import IsAdmin, IsAdminOrEntity
from accounts.utils import api_response
from .models import BloodStock
from .serializers import BloodStockSerializer, BloodStockAdjustSerializer
from donors.models import Donor
from donations.models import Donation
from entities.models import Entity
from notifications.utils import send_notification


class BloodStockView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request):
        if request.user.is_superuser or request.user.role == 'admin':
            stock = BloodStock.objects.select_related('entity').all()
        else:
            stock = request.user.entity_profile.blood_stock.select_related('entity').all()
        return api_response("success", "Blood stock retrieved.", BloodStockSerializer(stock, many=True).data)


class LowStockAlertView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request):
        if request.user.is_superuser or request.user.role == 'admin':
            stock = BloodStock.objects.select_related('entity').all()
        else:
            stock = request.user.entity_profile.blood_stock.select_related('entity').all()
        low_stock = [s for s in stock if s.is_low]
        return api_response("success", "Low stock alerts retrieved.", BloodStockSerializer(low_stock, many=True).data)


class BloodStockAdjustView(APIView):
    # Entity manually adjusts blood stock e.g. blood used or expired
    permission_classes = (IsAdminOrEntity,)

    def patch(self, request, pk):
        try:
            stock = BloodStock.objects.get(pk=pk)
        except BloodStock.DoesNotExist:
            return api_response("error", "Stock record not found.", None, 404)

        if request.user.role == 'entity' and stock.entity != request.user.entity_profile:
            return api_response("error", "You do not have access to this stock.", None, 403)

        serializer = BloodStockAdjustSerializer(stock, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        serializer.save()
        stock.refresh_from_db()
        if stock.is_low:
            send_notification(
                stock.entity.user,
                "Low Blood Stock Alert",
                f"Blood type {stock.blood_type} at {stock.entity.entity_name} is running low ({stock.units_available} unit(s) remaining)."
            )
        return api_response("success", "Blood stock updated.", BloodStockSerializer(stock).data)


class AdminStatsView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        stats = {
            "total_entities": Entity.objects.count(),
            "pending_entities": Entity.objects.filter(status='pending').count(),
            "approved_entities": Entity.objects.filter(status='approved').count(),
            "rejected_entities": Entity.objects.filter(status='rejected').count(),
            "total_donors": Donor.objects.count(),
            "eligible_donors": Donor.objects.filter(eligible=True).count(),
            "total_donations": Donation.objects.count(),
            "completed_donations": Donation.objects.filter(status='completed').count(),
            "pending_donations": Donation.objects.filter(status='pending').count(),
            "rejected_donations": Donation.objects.filter(status='rejected').count(),
            "low_stock_count": sum(1 for s in BloodStock.objects.all() if s.is_low),
        }
        return api_response("success", "Stats retrieved.", stats)
