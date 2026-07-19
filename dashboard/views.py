from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from entities.models import Entity
from donors.models import Donor, DonorCard
from donations.models import Donation
from inventory.models import BloodStock
from notifications.utils import send_notification


def dashboard_login(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return _redirect_by_role(user)
        return render(request, 'dashboard/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'dashboard/login.html')


@login_required(login_url='dashboard-login')
def dashboard_logout(request):
    logout(request)
    return redirect('dashboard-login')


def _redirect_by_role(user):
    if user.role == 'admin' or user.is_superuser:
        return redirect('admin-dashboard')
    elif user.role == 'entity':
        return redirect('entity-dashboard')
    elif user.role == 'donor':
        return redirect('donor-dashboard')
    return redirect('dashboard-login')


# ── Admin Views ──────────────────────────────────────────────

@login_required(login_url='dashboard-login')
def admin_dashboard(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard-login')
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_entities': Entity.objects.count(),
        'pending_entities': Entity.objects.filter(status='pending').count(),
        'total_donors': Donor.objects.count(),
        'total_donations': Donation.objects.count(),
        'pending_list': Entity.objects.filter(status='pending'),
    })


@login_required(login_url='dashboard-login')
def admin_entities(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard-login')
    return render(request, 'dashboard/admin_entities.html', {
        'entities': Entity.objects.all(),
    })


@login_required(login_url='dashboard-login')
def admin_approve_entity(request, pk):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard-login')
    if request.method == 'POST':
        entity = get_object_or_404(Entity, pk=pk)
        entity.status = request.POST.get('status')
        entity.registered_by = request.user
        entity.save()
        send_notification(
            entity.user,
            f"Entity {entity.status.capitalize()}",
            f"Your entity '{entity.entity_name}' has been {entity.status} by admin."
        )
        messages.success(request, f"{entity.entity_name} has been {entity.status}.")
    return redirect('admin-entities')


@login_required(login_url='dashboard-login')
def admin_donors(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard-login')
    return render(request, 'dashboard/admin_donors.html', {
        'donors': Donor.objects.select_related('entity').all(),
    })


@login_required(login_url='dashboard-login')
def admin_donations(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard-login')
    return render(request, 'dashboard/admin_donations.html', {
        'donations': Donation.objects.select_related('donor', 'entity').all(),
    })


@login_required(login_url='dashboard-login')
def admin_inventory(request):
    if not (request.user.role == 'admin' or request.user.is_superuser):
        return redirect('dashboard-login')
    return render(request, 'dashboard/admin_inventory.html', {
        'stocks': BloodStock.objects.select_related('entity').all(),
    })


# ── Entity Views ─────────────────────────────────────────────

@login_required(login_url='dashboard-login')
def entity_dashboard(request):
    if request.user.role != 'entity':
        return redirect('dashboard-login')
    try:
        entity = request.user.entity_profile
    except Entity.DoesNotExist:
        messages.warning(request, 'Please complete your entity profile via the API first.')
        return redirect('dashboard-login')
    stocks = entity.blood_stock.all()
    return render(request, 'dashboard/entity_dashboard.html', {
        'entity': entity,
        'total_donors': entity.donors.count(),
        'total_donations': entity.donations.count(),
        'total_stock': stocks.count(),
        'low_stock_count': sum(1 for s in stocks if s.is_low),
        'recent_donations': entity.donations.select_related('donor').order_by('-donation_date')[:10],
    })


@login_required(login_url='dashboard-login')
def entity_donors(request):
    if request.user.role != 'entity':
        return redirect('dashboard-login')
    return render(request, 'dashboard/entity_donors.html', {
        'donors': request.user.entity_profile.donors.all(),
    })


@login_required(login_url='dashboard-login')
def entity_donations(request):
    if request.user.role != 'entity':
        return redirect('dashboard-login')
    return render(request, 'dashboard/entity_donations.html', {
        'donations': request.user.entity_profile.donations.select_related('donor').all(),
    })


@login_required(login_url='dashboard-login')
def entity_inventory(request):
    if request.user.role != 'entity':
        return redirect('dashboard-login')
    return render(request, 'dashboard/entity_inventory.html', {
        'stocks': request.user.entity_profile.blood_stock.all(),
    })


@login_required(login_url='dashboard-login')
def entity_cards(request):
    if request.user.role != 'entity':
        return redirect('dashboard-login')
    return render(request, 'dashboard/entity_cards.html', {
        'cards': request.user.entity_profile.issued_cards.select_related('donor').all(),
        'today': timezone.now().date(),
    })


# ── Donor Views ──────────────────────────────────────────────

@login_required(login_url='dashboard-login')
def donor_dashboard(request):
    if request.user.role != 'donor':
        return redirect('dashboard-login')
    try:
        donor = request.user.donor_profile
    except Donor.DoesNotExist:
        messages.warning(request, 'Donor profile not found.')
        return redirect('dashboard-login')
    return render(request, 'dashboard/donor_dashboard.html', {
        'donor': donor,
        'total_donations': donor.donations.count(),
        'donations': donor.donations.select_related('entity').order_by('-donation_date'),
    })
