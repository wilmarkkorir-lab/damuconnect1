from django.urls import path
from .views import DonationListCreateView, DonationDetailView, DonorDonationHistoryView, DonationExportCSVView

urlpatterns = [
    path('', DonationListCreateView.as_view(), name='donation-list-create'),
    path('<int:pk>/', DonationDetailView.as_view(), name='donation-detail'),
    path('history/', DonorDonationHistoryView.as_view(), name='donation-history'),
    path('export/', DonationExportCSVView.as_view(), name='donation-export'),
]
