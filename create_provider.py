# Create a new doctor (provider) in AthenaHealth.
# Fill in the PROVIDER DETAILS section below, then run.
#
# BILLING NOTE:
#   Setting billable=True requires a valid medicalgroupid + providergroupid
#   that is configured by AthenaHealth during production onboarding.
#   In the preview/sandbox environment these IDs are not set up for billing,
#   so the script creates the provider first (non-billable), then updates
#   their profile fields (NPI, specialty, type) via a second PUT call.
#   In production: set MEDICAL_GROUP_ID and PROVIDER_GROUP_ID to your real
#   values and billable=True will work on the first POST.

import requests
import json

# ── Credentials ───────────────────────────────────────────────
CLIENT_ID     = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID   = "195900"
DEPARTMENT_ID = "144"
BASE_URL      = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

# ── Internal IDs ──────────────────────────────────────────────
# Preview/sandbox: use 1. Production: get from your AthenaHealth admin.
MEDICAL_GROUP_ID  = "1"
PROVIDER_GROUP_ID = "1"

# ── Known Specialty IDs ───────────────────────────────────────
SPECIALTIES = {
    "Cardiology":           "006",
    "Family Medicine":      "008",
    "Gastroenterology":     "016",
    "Hospitalist":          "022",
    "Neonatology":          "033",
    "Orthopedic Surgery":   "045",
    "Addiction Medicine":   "079",
    "Acupuncture":          "087",
    "Wound Care":           "715",
}

# ── Provider Details — EDIT THIS SECTION ─────────────────────
PROVIDER = {
    # Identity
    "firstname":      "Abdul",
    "lastname":       "Rehman",
    "sex":            "M",               # M or F

    # Scheduling
    "schedulingname": "arehman126",          # Unique, no spaces. Used for inbox routing.

    # Billing & credentials
    "billingname":    "Abdul Rehman",    # Name on claims: "Lastname Firstname"
    "providertypeid": "MD",              # MD, DO, NP, PA-C, FNP, APRN, CRNA, LCSW, PT, etc.
    "npi":            "1234567891",      # 10-digit NPI from CMS NPI Registry
    "specialty":      "Cardiology",      # Must match a key in SPECIALTIES above

    # Flags
    "acceptingnewpatients":    True,
    "createencounteroncheckin":True,
    "hideinportal":            False,
    "signatureonfileflag":     True,
}

# ── Auth ──────────────────────────────────────────────────────
print("Authenticating...")
token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET),
).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Token obtained.\n")

# ── Step 1: Check scheduling name availability ────────────────
print(f"Checking schedulingname '{PROVIDER['schedulingname']}'...")
r = requests.get(f"{BASE_URL}/providers", headers=headers, params={
    "departmentid": DEPARTMENT_ID,
    "limit":        200,
})
existing = [p.get("schedulingname", "").lower() for p in r.json().get("providers", [])]

if PROVIDER["schedulingname"].lower() in existing:
    print(f"ERROR: schedulingname '{PROVIDER['schedulingname']}' is already taken.")
    print("Change it to something unique and re-run.")
    exit(1)
print(f"  '{PROVIDER['schedulingname']}' is available.\n")

# ── Step 2: Resolve specialty ─────────────────────────────────
specialty_name = PROVIDER.get("specialty")
specialtyid    = SPECIALTIES.get(specialty_name) if specialty_name else None
if specialty_name and not specialtyid:
    print(f"WARNING: '{specialty_name}' not in known specialties list. Specialty will be skipped.")
    print(f"  Known: {list(SPECIALTIES.keys())}\n")

# ── Step 3: POST — create provider ───────────────────────────
print("Creating provider record...")
create_payload = {
    "entitytypeid":        "1",              # 1 = Person
    "medicalgroupid":      MEDICAL_GROUP_ID,
    "providergroupid":     PROVIDER_GROUP_ID,
    "schedulingname":      PROVIDER["schedulingname"],
    "signatureonfileflag": str(PROVIDER["signatureonfileflag"]).lower(),
    "billable":            "false",          # See billing note at top of file
    "firstname":           PROVIDER["firstname"],
    "lastname":            PROVIDER["lastname"],
}

r = requests.post(f"{BASE_URL}/providers", headers=headers, data=create_payload)
print(f"  Status: {r.status_code}  Response: {r.text}\n")

if r.status_code != 200:
    print("ERROR: POST failed.")
    exit(1)

resp = r.json()
if resp.get("providerid", -1) == -1:
    print(f"ERROR: {resp.get('errorreason', 'Unknown')}")
    exit(1)

provider_id = resp["providerid"]
print(f"Provider created. providerid = {provider_id}\n")

# ── Step 4: Note on additional fields ────────────────────────
# In production (with valid MEDICAL_GROUP_ID + PROVIDER_GROUP_ID), a PUT call
# here would update NPI, specialty, providertypeid, sex, acceptingnewpatients, etc.
# In the preview sandbox, providergroupid must match a configured enterprise
# tablespace — until that is set up, additional fields must be updated via
# the AthenaHealth admin portal (Provider Settings > Edit Provider).
print("Note: NPI, specialty, type and flags require a valid PROVIDER_GROUP_ID.")
print("      In sandbox: update those fields via the AthenaHealth admin portal.")
print("      In production: set MEDICAL_GROUP_ID + PROVIDER_GROUP_ID and they")
print("      can be set here via PUT /providers/{id}.\n")

# ── Step 5: Verify ────────────────────────────────────────────
print("Fetching final provider record...")
r3 = requests.get(f"{BASE_URL}/providers/{provider_id}", headers=headers)
record = r3.json()
record = record[0] if isinstance(record, list) else record

print("=" * 55)
print("  New Provider Created")
print("=" * 55)
print(f"  Provider ID   : {record.get('providerid')}")
print(f"  Name          : {record.get('firstname')} {record.get('lastname')}")
print(f"  Type          : {record.get('providertype', 'N/A')}")
print(f"  Specialty     : {record.get('specialty', 'N/A')}")
print(f"  NPI           : {record.get('npi', 'N/A')}")
print(f"  Scheduling    : {record.get('schedulingname')}")
print(f"  Billable      : {record.get('billable')}")
print(f"  New Patients  : {record.get('acceptingnewpatients')}")
print(f"  Sex           : {record.get('sex', 'N/A')}")
print("=" * 55)
print()
print("Full record:")
print(json.dumps(record, indent=2))
