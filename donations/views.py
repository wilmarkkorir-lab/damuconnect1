from rest_framework.views import APIView
from accounts.permissions import IsDonor, IsAdminOrEntity
from accounts.utils import api_response
from .models import Donation
from .serializers import DonationSerializer, RecordDonationSerializer, UpdateDonationSerializer
from notifications.utils import send_notification


class DonationListCreateView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request):
        donations = Donation.objects.select_related('donor', 'entity').all()

        # Filter by status e.g. ?status=completed
        status = request.query_params.get('status')
        if status:
            donations = donations.filter(status=status)

        # Filter by blood type e.g. ?blood_type=O+
        blood_type = request.query_params.get('blood_type')
        if blood_type:
            donations = donations.filter(donor__blood_type=blood_type)

        # Filter by date e.g. ?date=2024-01-01
        date = request.query_params.get('date')
        if date:
            donations = donations.filter(donation_date=date)

        return api_response("success", "Donations retrieved.", DonationSerializer(donations, many=True).data)

    def post(self, request):
        if request.user.role != 'entity':
            return api_response("error", "Only entities can record donations.", None, 403)
        serializer = RecordDonationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        donation = serializer.save()
        # Notify donor if they have a user account
        if donation.donor.user:
            send_notification(
                donation.donor.user,
                "Donation Recorded",
                f"A donation of {donation.quantity} unit(s) has been recorded at {donation.entity.entity_name}."
            )
        return api_response("success", "Donation recorded.", DonationSerializer(donation).data, 201)


class DonationDetailView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request, pk):
        try:
            donation = Donation.objects.get(pk=pk)
        except Donation.DoesNotExist:
            return api_response("error", "Donation not found.", None, 404)
        return api_response("success", "Donation retrieved.", DonationSerializer(donation).data)

    def patch(self, request, pk):
        # Only entity can update donation status
        if request.user.role != 'entity':
            return api_response("error", "Only entities can update donations.", None, 403)
        try:
            donation = Donation.objects.get(pk=pk, entity=request.user.entity_profile)
        except Donation.DoesNotExist:
            return api_response("error", "Donation not found.", None, 404)
        serializer = UpdateDonationSerializer(donation, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        donation = serializer.save()
        return api_response("success", "Donation updated.", DonationSerializer(donation).data)


class DonorDonationHistoryView(APIView):
    permission_classes = (IsDonor,)

    def get(self, request):
        try:
            donations = request.user.donor_profile.donations.all()
        except Exception:
            return api_response("error", "Donor profile not found.", None, 404)
        return api_response("success", "Donation history retrieved.", DonationSerializer(donations, many=True).data)
