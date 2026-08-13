from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Auth — register, login, logout, refresh, profile
    path('api/auth/', include('accounts.urls')),

    # Entities — admin approves/rejects, entity manages profile
    path('api/entities/', include('entities.urls')),

    # Donors — entity registers donors, issues cards
    path('api/donors/', include('donors.urls')),

    # Donations — entity records donations, donor views history
    path('api/donations/', include('donations.urls')),

    # Inventory — blood stock levels and low stock alerts
    path('api/inventory/', include('inventory.urls')),

    # Dashboard — browser UI for admin, entity, donor
    path('dashboard/', include('dashboard.urls')),

    # API schema needed for docs to work
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Notifications — user views and marks notifications
    path('api/notifications/', include('notifications.urls')),

    # Chatbot — general and smart chat
    path('api/chat/', include('chatbot.urls')),

    # Audit logs — admin views system activity
    path('api/audit/', include('audit.urls')),

    # Swagger docs
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
