from django.urls import path
from .views import EntityProfileView, AdminEntityListView, AdminEntityApprovalView, AdminDeactivateUserView

urlpatterns = [
    path('', AdminEntityListView.as_view(), name='admin-entity-list'),                      # GET
    path('profile/', EntityProfileView.as_view(), name='entity-profile'),                   # GET/POST/PATCH
    path('<int:pk>/approval/', AdminEntityApprovalView.as_view(), name='entity-approval'),  # PATCH
    path('users/<int:pk>/deactivate/', AdminDeactivateUserView.as_view(), name='deactivate-user'),  # PATCH
]
