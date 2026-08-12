from django.urls import path
from .views import DonorListCreateView, DonorDetailView, DonorProfileView, IssueCardView, DonorCardListView, DonorCardDeleteView, DonorMyCardsView, DonorCreateOwnProfileView

urlpatterns = [
    path('', DonorListCreateView.as_view(), name='donor-list-create'),
    path('<int:pk>/', DonorDetailView.as_view(), name='donor-detail'),
    path('profile/', DonorProfileView.as_view(), name='donor-profile'),
    path('profile/create/', DonorCreateOwnProfileView.as_view(), name='donor-create-own-profile'),
    path('cards/', DonorCardListView.as_view(), name='donor-card-list'),
    path('cards/issue/', IssueCardView.as_view(), name='issue-card'),
    path('cards/<int:pk>/delete/', DonorCardDeleteView.as_view(), name='donor-card-delete'),
    path('my-cards/', DonorMyCardsView.as_view(), name='donor-my-cards'),
]
