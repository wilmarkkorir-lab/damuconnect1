import os
from django.conf import settings
from groq import Groq
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.utils import api_response

# Initialize Groq client only if API key is configured
client = None
if settings.GROQ_API_KEY:
    client = Groq(api_key=settings.GROQ_API_KEY)


def ask_groq(system_prompt, user_message):
    """Send a message to Groq and return the reply."""
    if not client:
        raise Exception("AI service is not configured. Please contact the administrator.")
    chat = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    reply = chat.choices[0].message.content
    # Strip thinking tags that some models include
    if "</think>" in reply:
        reply = reply.split("</think>")[-1].strip()
    if "<think>" in reply:
        reply = reply.split("<think>")[0].strip()
    return reply.strip()


def get_admin_data():
    """Fetch system-wide data for admin."""
    from entities.models import Entity
    from donors.models import Donor
    from donations.models import Donation
    from inventory.models import BloodStock

    entities = Entity.objects.all()
    stock = BloodStock.objects.all()

    return {
        "total_entities": entities.count(),
        "pending_entities": entities.filter(status='pending').count(),
        "approved_entities": entities.filter(status='approved').count(),
        "rejected_entities": entities.filter(status='rejected').count(),
        "total_donors": Donor.objects.count(),
        "eligible_donors": Donor.objects.filter(eligible=True).count(),
        "total_donations": Donation.objects.count(),
        "completed_donations": Donation.objects.filter(status='completed').count(),
        "pending_donations": Donation.objects.filter(status='pending').count(),
        "low_stock_items": [
            f"{s.entity.entity_name} - {s.blood_type}: {s.units_available} units"
            for s in stock if s.is_low
        ],
        "all_stock": [
            f"{s.entity.entity_name} - {s.blood_type}: {s.units_available} units"
            for s in stock
        ],
        "entities_list": [
            f"{e.entity_name} ({e.entity_type}) - {e.status}"
            for e in entities
        ],
    }


def get_entity_data(user):
    """Fetch data for a specific entity."""
    from inventory.models import BloodStock

    try:
        entity = user.entity_profile
    except Exception:
        return {}

    donors = entity.donors.all()
    donations = entity.donations.all()
    stock = entity.blood_stock.all()

    return {
        "entity_name": entity.entity_name,
        "entity_type": entity.entity_type,
        "entity_status": entity.status,
        "total_donors": donors.count(),
        "eligible_donors": donors.filter(eligible=True).count(),
        "ineligible_donors": donors.filter(eligible=False).count(),
        "donors_list": [
            f"{d.full_name} - {d.blood_type} - {'Eligible' if d.eligible else 'Not Eligible'}"
            for d in donors
        ],
        "total_donations": donations.count(),
        "completed_donations": donations.filter(status='completed').count(),
        "pending_donations": donations.filter(status='pending').count(),
        "blood_stock": [
            f"{s.blood_type}: {s.units_available} units {'(LOW)' if s.is_low else ''}"
            for s in stock
        ],
        "low_stock": [
            f"{s.blood_type}: {s.units_available} units"
            for s in stock if s.is_low
        ],
    }


def get_donor_data(user):
    """Fetch data for a specific donor."""
    try:
        donor = user.donor_profile
    except Exception:
        return {}

    donations = donor.donations.all()

    return {
        "full_name": donor.full_name,
        "blood_type": donor.blood_type,
        "eligible": donor.eligible,
        "date_of_birth": str(donor.date_of_birth),
        "last_donation_date": str(donor.last_donation_date) if donor.last_donation_date else "Never donated",
        "total_donations": donations.count(),
        "entity": donor.entity.entity_name,
        "donation_history": [
            f"{d.donation_date} - {d.quantity} unit(s) - {d.status}"
            for d in donations
        ],
    }


class GeneralChatView(APIView):
    """Anyone can ask general blood donation questions — no token needed."""
    permission_classes = (AllowAny,)

    def post(self, request):
        message = request.data.get("message", "").strip()
        if not message:
            return api_response("error", "Message is required.", None, 400)

        system_prompt = """You are a strict blood donation assistant for DamuConnect, Kenya's national blood management system.

RULES:
1. ONLY answer questions about: blood donation, blood types, eligibility, donation process, hospitals, blood banks, clinics, inventory, donors, and how to use the DamuConnect system.
2. If asked about anything else (politics, sports, religion, cooking, travel, entertainment, general knowledge, etc.), politely refuse and redirect: "I only help with blood donation and DamuConnect system questions. Ask me about eligibility, blood types, or how to use the system."
3. Keep answers SHORT — maximum 2 sentences. Be direct and factual.
4. Never make up information. If unsure, say "I don't have that information. Please contact your hospital or blood bank."
5. For DamuConnect system questions, guide users: "Go to [section name] in your dashboard" or "Contact your entity admin."

TONE: Professional, brief, helpful."""

        try:
            reply = ask_groq(system_prompt, message)
            return api_response("success", "Response received.", {"reply": reply})
        except Exception as e:
            return api_response("error", str(e), None, 500)


class SmartChatView(APIView):
    """Logged in users ask questions about their own system data."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        message = request.data.get("message", "").strip()
        if not message:
            return api_response("error", "Message is required.", None, 400)

        user = request.user

        # Fetch data based on role
        if user.is_superuser or user.role == 'admin':
            data = get_admin_data()
            role_context = "You are assisting a system admin."
        elif user.role == 'entity':
            data = get_entity_data(user)
            role_context = f"You are assisting an entity user managing {data.get('entity_name', 'their facility')}."
        elif user.role == 'donor':
            data = get_donor_data(user)
            role_context = f"You are assisting a blood donor named {data.get('full_name', 'the user')}."
        else:
            return api_response("error", "Unknown role.", None, 403)

        system_prompt = f"""You are a strict assistant for DamuConnect, Kenya's national blood management system. {role_context}

RULES:
1. ONLY answer questions about: blood donation, blood types, eligibility, donation process, hospitals, blood banks, clinics, inventory, donors, and how to use the DamuConnect system.
2. If asked about anything else (politics, sports, religion, cooking, travel, entertainment, general knowledge, etc.), politely refuse: "I only help with blood donation and DamuConnect system questions."
3. Use ONLY the provided system data below. Do NOT make up information. If the data doesn't contain the answer, say: "I don't have that information. Please check your dashboard or contact your admin."
4. Keep answers SHORT — maximum 2 sentences. Be direct and factual.
5. For system navigation questions, guide users to the correct dashboard section.

SYSTEM DATA:
{data}

TONE: Professional, brief, helpful."""

        try:
            reply = ask_groq(system_prompt, message)
            return api_response("success", "Response received.", {"reply": reply})
        except Exception as e:
            return api_response("error", str(e), None, 500)
