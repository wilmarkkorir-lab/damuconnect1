from django.urls import path
from .views import BloodStockView, LowStockAlertView, BloodStockAdjustView, AdminStatsView

urlpatterns = [
    path('', BloodStockView.as_view(), name='blood-stock'),                     # GET
    path('alerts/', LowStockAlertView.as_view(), name='low-stock-alerts'),      # GET
    path('<int:pk>/adjust/', BloodStockAdjustView.as_view(), name='stock-adjust'),  # PATCH
    path('stats/', AdminStatsView.as_view(), name='admin-stats'),               # GET admin only
]
