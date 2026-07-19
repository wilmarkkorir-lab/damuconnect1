from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.dashboard_login, name='dashboard-login'),
    path('logout/', views.dashboard_logout, name='dashboard-logout'),

    # Admin
    path('admin/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/entities/', views.admin_entities, name='admin-entities'),
    path('admin/entities/<int:pk>/approve/', views.admin_approve_entity, name='admin-approve-entity'),
    path('admin/donors/', views.admin_donors, name='admin-donors'),
    path('admin/donations/', views.admin_donations, name='admin-donations'),
    path('admin/inventory/', views.admin_inventory, name='admin-inventory'),

    # Entity
    path('entity/', views.entity_dashboard, name='entity-dashboard'),
    path('entity/donors/', views.entity_donors, name='entity-donors'),
    path('entity/donations/', views.entity_donations, name='entity-donations'),
    path('entity/inventory/', views.entity_inventory, name='entity-inventory'),
    path('entity/cards/', views.entity_cards, name='entity-cards'),

    # Donor
    path('donor/', views.donor_dashboard, name='donor-dashboard'),
]
