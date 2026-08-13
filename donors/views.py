from rest_framework.views import APIView
from accounts.permissions import IsDonor, IsAdminOrEntity
from accounts.utils import api_response
from .models import Donor, DonorCard
from .serializers import DonorSerializer, DonorRegisterSerializer, DonorUpdateSerializer, DonorCardSerializer, IssueCardSerializer
from notifications.utils import send_notification
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework.pagination import PageNumberPagination
import csv
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination


class DonorPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


def check_donor_eligibility(donor):
    age = relativedelta(timezone.now().date(), donor.date_of_birth).years
    if age < 18:
        eligible = False
    elif donor.last_donation_date:
        diff = relativedelta(timezone.now().date(), donor.last_donation_date)
        eligible = not (diff.years == 0 and diff.months < 3)
    else:
        eligible = True
    if donor.eligible != eligible:
        donor.eligible = eligible
        donor.save()


class DonorListCreateView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request):
        donors = Donor.objects.select_related('entity').all()

        search = self.request.query_params.get('search')
        if search:
            donors = donors.filter(full_name__icontains=search) | donors.filter(blood_type__icontains=search)

        blood_type = self.request.query_params.get('blood_type')
        if blood_type:
            donors = donors.filter(blood_type=blood_type)

        eligible = self.request.query_params.get('eligible')
        if eligible is not None:
            donors = donors.filter(eligible=eligible.lower() == 'true')

        paginator = DonorPagination()
        page = paginator.paginate_queryset(donors, request)
        serializer = DonorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = DonorRegisterSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        donor = serializer.save()
        check_donor_eligibility(donor)
        return api_response("success", "Donor registered.", DonorSerializer(donor).data, 201)


class DonorDetailView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request, pk):
        try:
            donor = Donor.objects.get(pk=pk)
        except Donor.DoesNotExist:
            return api_response("error", "Donor not found.", None, 404)
        check_donor_eligibility(donor)
        return api_response("success", "Donor retrieved.", DonorSerializer(donor).data)

    def patch(self, request, pk):
        try:
            donor = Donor.objects.get(pk=pk)
        except Donor.DoesNotExist:
            return api_response("error", "Donor not found.", None, 404)
        serializer = DonorUpdateSerializer(donor, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        donor = serializer.save()
        check_donor_eligibility(donor)
        return api_response("success", "Donor updated.", DonorSerializer(donor).data)

    def delete(self, request, pk):
        try:
            donor = Donor.objects.get(pk=pk)
        except Donor.DoesNotExist:
            return api_response("error", "Donor not found.", None, 404)
        donor.delete()
        return api_response("success", "Donor deleted.", None)


class DonorProfileView(APIView):
    permission_classes = (IsDonor,)

    def get(self, request):
        try:
            donor = request.user.donor_profile
        except Donor.DoesNotExist:
            return api_response("error", "Donor profile not found.", None, 404)
        check_donor_eligibility(donor)
        return api_response("success", "Profile retrieved.", DonorSerializer(donor).data)


class IssueCardView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def post(self, request):
        serializer = IssueCardSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response("error", "Invalid data.", serializer.errors, 400)
        card = serializer.save()
        # Notify donor if they have a user account
        if card.donor.user:
            send_notification(
                card.donor.user,
                "Donor Card Issued",
                f"Your donor card ({card.card_number}) has been issued by {card.entity.entity_name}. It expires on {card.expiry_date}."
            )
        return api_response("success", "Donor card issued.", DonorCardSerializer(card).data, 201)


class DonorCardListView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request):
        if request.user.is_superuser or request.user.role == 'admin':
            cards = DonorCard.objects.select_related('donor', 'entity').all()
        else:
            cards = request.user.entity_profile.issued_cards.select_related('donor', 'entity').all()

        expired = request.query_params.get('expired')
        if expired is not None:
            today = date.today()
            if expired.lower() == 'true':
                cards = [c for c in cards if c.expiry_date < today]
            else:
                cards = [c for c in cards if c.expiry_date >= today]

        return api_response("success", "Cards retrieved.", DonorCardSerializer(cards, many=True).data)


class DonorCardDeleteView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def delete(self, request, pk):
        try:
            card = DonorCard.objects.get(pk=pk)
        except DonorCard.DoesNotExist:
            return api_response("error", "Card not found.", None, 404)
        if request.user.role == 'entity' and card.entity != request.user.entity_profile:
            return api_response("error", "You do not have access to this card.", None, 403)
        card.delete()
        return api_response("success", "Donor card deleted.", None)


class DonorMyCardsView(APIView):
    permission_classes = (IsDonor,)

    def get(self, request):
        try:
            donor = request.user.donor_profile
        except Donor.DoesNotExist:
            return api_response("error", "Donor profile not found.", None, 404)
        cards = donor.cards.select_related('donor', 'entity').all()
        return api_response("success", "Cards retrieved.", DonorCardSerializer(cards, many=True).data)


class DonorExportCSVView(APIView):
    permission_classes = (IsAdminOrEntity,)

    def get(self, request):
        donors = Donor.objects.select_related('entity').all()

        search = request.query_params.get('search')
        if search:
            donors = donors.filter(full_name__icontains=search) | donors.filter(blood_type__icontains=search)

        blood_type = request.query_params.get('blood_type')
        if blood_type:
            donors = donors.filter(blood_type=blood_type)

        eligible = request.query_params.get('eligible')
        if eligible is not None:
            donors = donors.filter(eligible=eligible.lower() == 'true')

        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="donors_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Full Name', 'Email', 'Phone', 'Blood Type', 'Date of Birth', 'Last Donation', 'Eligible', 'Entity'])

        for donor in donors:
            writer.writerow([
                donor.full_name,
                donor.email,
                donor.phone,
                donor.blood_type,
                donor.date_of_birth,
                donor.last_donation_date or 'Never',
                'Yes' if donor.eligible else 'No',
                donor.entity.entity_name if donor.entity else 'N/A',
            ])

        return response
