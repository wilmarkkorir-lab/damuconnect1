from django.urls import path
from .views import DonationListCreateView, DonationDetailView, DonorDonationHistoryView

urlpatterns = [
    path('', DonationListCreateView.as_view(), name='donation-list-create'),        # GET/POST
    path('<int:pk>/', DonationDetailView.as_view(), name='donation-detail'),        # GET/PATCH
    path('history/', DonorDonationHistoryView.as_view(), name='donation-history'),  # GET donor history
]
