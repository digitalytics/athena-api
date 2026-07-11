import requests
import json
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

CLIENT_ID = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID = "195900"
BASE_URL = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET)
).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# ── Build realistic referral PDF ─────────────────────────────
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=letter)
width, height = letter

def draw_line(canvas, y):
    canvas.setStrokeColor(colors.grey)
    canvas.line(50, y, width - 50, y)

def section_header(canvas, text, y):
    canvas.setFillColor(colors.HexColor("#2C3E50"))
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(50, y, text)
    draw_line(canvas, y - 5)
    canvas.setFillColor(colors.black)

def field(canvas, label, value, x, y):
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(x, y, f"{label}:")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(x + 130, y, value)

# ── Title ────────────────────────────────────────────────────
c.setFillColor(colors.HexColor("#2C3E50"))
c.setFont("Helvetica-Bold", 18)
c.drawCentredString(width / 2, height - 50, "PATIENT REFERRAL FORM")
c.setFont("Helvetica", 9)
c.setFillColor(colors.grey)
c.drawCentredString(width / 2, height - 65, "Please complete all sections. Fax to receiving provider.")
c.setFillColor(colors.black)

# ── Section 1: Patient Information ───────────────────────────
y = height - 100
section_header(c, "SECTION 1 — PATIENT INFORMATION", y)

y -= 25
field(c, "First Name",           "Sarah",              50,  y)
field(c, "Last Name",            "Johnson",            300, y)

y -= 18
field(c, "Date of Birth",        "03/22/1990",         50,  y)
field(c, "Sex",                  "F",                  300, y)

y -= 18
field(c, "Phone (Mobile)",       "(617) 555-1234",     50,  y)
field(c, "Phone (Home)",         "(617) 555-5678",     300, y)

y -= 18
field(c, "Email",                "sarah.johnson@email.com", 50, y)

y -= 18
field(c, "Address",              "742 Evergreen Terrace", 50, y)

y -= 18
field(c, "City",                 "Springfield",        50,  y)
field(c, "State",                "MA",                 300, y)

y -= 18
field(c, "ZIP Code",             "01101",              50,  y)

# ── Section 2: Referring Provider ────────────────────────────
y -= 35
section_header(c, "SECTION 2 — REFERRING PROVIDER", y)

y -= 25
field(c, "Provider Name",        "Dr. Michael Chen",   50,  y)
field(c, "NPI",                  "1234567890",         300, y)

y -= 18
field(c, "Practice Name",        "Springfield Family Medicine", 50, y)

y -= 18
field(c, "Phone",                "(617) 555-1234",     50,  y)
field(c, "Fax",                  "(617) 555-5678",     300, y)

y -= 18
field(c, "Address",              "100 Medical Plaza, Springfield, MA 01101", 50, y)

# ── Section 3: Referral Details ───────────────────────────────
y -= 35
section_header(c, "SECTION 3 — REFERRAL DETAILS", y)

y -= 25
field(c, "Referred To",          "Cardiology Department",     50, y)
field(c, "Urgency",              "Routine",                   300, y)

y -= 18
field(c, "Reason for Referral",  "Chest pain, exertional dyspnea, rule out CAD", 50, y)

y -= 18
field(c, "Primary Diagnosis",    "Chest Pain (ICD-10: R07.9)",       50, y)

y -= 18
field(c, "Secondary Diagnosis",  "Hypertension (ICD-10: I10)",       50, y)

y -= 18
field(c, "Date of Service",      "07/10/2026",         50,  y)
field(c, "Auth Number",          "AUTH-2026-44821",    300, y)

y -= 25
c.setFont("Helvetica-Bold", 9)
c.drawString(50, y, "Clinical Notes:")
c.setFont("Helvetica", 9)
notes = "Patient presents with 3-month history of exertional chest pain and shortness of breath. "
notes += "EKG showed non-specific ST changes. Stress test pending. Refer for cardiology evaluation."
c.drawString(50, y - 15, notes[:90])
c.drawString(50, y - 28, notes[90:])

# ── Section 4: Insurance ──────────────────────────────────────
y -= 65
section_header(c, "SECTION 4 — INSURANCE INFORMATION", y)

y -= 25
field(c, "Primary Payer",        "Blue Cross Blue Shield",    50, y)
field(c, "Plan Type",            "PPO",                       300, y)

y -= 18
field(c, "Policy Number",        "BCB-987654321",             50, y)
field(c, "Group ID",             "GRP-00456",                 300, y)

y -= 18
field(c, "Policy Holder Name",   "Sarah Johnson",             50, y)
field(c, "Relationship",         "Self",                      300, y)

y -= 18
field(c, "Policy Holder DOB",    "03/22/1990",                50, y)

# ── Section 5: Guarantor ──────────────────────────────────────
y -= 35
section_header(c, "SECTION 5 — GUARANTOR INFORMATION", y)

y -= 25
field(c, "Guarantor First Name", "Sarah",              50,  y)
field(c, "Guarantor Last Name",  "Johnson",            300, y)

y -= 18
field(c, "Guarantor DOB",        "03/22/1990",         50,  y)
field(c, "Relationship",         "1 (Self)",           300, y)

# ── Footer ───────────────────────────────────────────────────
c.setStrokeColor(colors.grey)
c.line(50, 60, width - 50, 60)
c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(width / 2, 45, "CONFIDENTIAL — This document contains protected health information (PHI).")
c.drawCentredString(width / 2, 33, "Unauthorized disclosure is prohibited under HIPAA.")

c.save()
buffer.seek(0)

print("Referral PDF created")

# ── Upload to athena inbox ────────────────────────────────────
response = requests.post(
    f"{BASE_URL}/documents/admin",
    headers=headers,
    files={"attachmentcontents": ("referral.pdf", buffer, "application/pdf")},
    data={
        "departmentid":  "144",
        "adminsubclass": "REFERRAL",
        "internalnote":  "Inbound referral - unmatched patient - Sarah Johnson",
        "documentroute": "FAX",
    }
)


print("Upload status:", response.status_code)

print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    admin_id = response.json()["adminid"]
    print(f"\nReferral uploaded. Admin ID: {admin_id}")
    print(f"View document: GET {BASE_URL}/documents/admin/{admin_id}")