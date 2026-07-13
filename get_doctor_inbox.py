# Fetch a doctor's full inbox from AthenaHealth.
# Covers two inbox types:
#   1. Admin documents (referrals, faxes) assigned to the doctor
#   2. Clinical chart tasks (per patient assigned to the doctor)
#
# Usage: set SEARCH_NAME or PROVIDER_ID below, then run.

import requests
import json

# ── Config ────────────────────────────────────────────────────
CLIENT_ID     = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID   = "195900"
DEPARTMENT_ID = "144"
BASE_URL      = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

# Set one of these to find your doctor:
SEARCH_NAME = "Alcatraz"   # partial last name search  (set to None to use PROVIDER_ID)
PROVIDER_ID = None         # use a known providerid directly (e.g. 2360)

# Date range for admin document inbox
INBOX_START = "01/01/2025"
INBOX_END   = "12/31/2026"

# ── Auth ──────────────────────────────────────────────────────
print("Authenticating...")
token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET)
).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}
print("Token obtained.\n")

# ── Step 1: Find the Doctor ───────────────────────────────────
def find_provider(name=None, provider_id=None):
    if provider_id:
        r = requests.get(f"{BASE_URL}/providers/{provider_id}", headers=headers)
        return r.json()[0]

    # Search by name across all providers (paginate up to 500)
    offset = 0
    while True:
        r = requests.get(f"{BASE_URL}/providers", headers=headers, params={
            "departmentid": DEPARTMENT_ID,
            "limit":        100,
            "offset":       offset,
        })
        data = r.json()
        providers = data.get("providers", [])
        if not providers:
            break

        for p in providers:
            full_name = f"{p.get('firstname','')} {p.get('lastname','')}".lower()
            if name.lower() in full_name:
                return p

        offset += 100
        if offset >= data.get("totalcount", 0):
            break

    return None

print(f"Looking up doctor: {SEARCH_NAME or f'ID={PROVIDER_ID}'}")
provider = find_provider(name=SEARCH_NAME, provider_id=PROVIDER_ID)

if not provider:
    print("Doctor not found. Check SEARCH_NAME or PROVIDER_ID.")
    exit(1)

provider_id      = provider["providerid"]
scheduling_name  = provider.get("schedulingname", "")
full_name        = f"Dr. {provider.get('firstname','')} {provider.get('lastname','')}"
specialty        = provider.get("specialty", "N/A")
username         = provider.get("providerusername", "N/A")

print("=" * 55)
print(f"  Doctor Found")
print("=" * 55)
print(f"  Name:            {full_name}")
print(f"  Provider ID:     {provider_id}")
print(f"  Username:        {username}")
print(f"  Scheduling Name: {scheduling_name}")
print(f"  Specialty:       {specialty}")
print(f"  NPI:             {provider.get('npi', 'N/A')}")
print("=" * 55)
print()

# ── Step 2: Admin Document Inbox (Referrals, Faxes) ──────────
print(f"Fetching admin document inbox (assigned to '{scheduling_name}')...")

admin_inbox = requests.get(
    f"{BASE_URL}/documents/admin",
    headers=headers,
    params={
        "departmentid":     DEPARTMENT_ID,
        "documentsubclass": "ADMIN_REFERRAL",
        "startdate":        INBOX_START,
        "enddate":          INBOX_END,
        "assignedto":       scheduling_name,
        "limit":            50,
    }
).json()

total_admin = admin_inbox.get("totalcount", 0)
print(f"  Admin inbox total: {total_admin} document(s)\n")

if total_admin > 0:
    print(f"  {'AdminID':<10} {'Status':<12} {'Subclass':<22} {'Created':<22} {'Priority'}")
    print(f"  {'-'*9:<10} {'-'*11:<12} {'-'*21:<22} {'-'*21:<22} {'-'*8}")
    for doc in admin_inbox.get("admins", []):
        print(
            f"  {doc.get('adminid',''):<10} "
            f"{doc.get('status',''):<12} "
            f"{doc.get('documentsubclass',''):<22} "
            f"{doc.get('createddatetime','')[:19]:<22} "
            f"{'HIGH' if doc.get('priority') == '1' else 'Normal'}"
        )
else:
    print("  No admin documents assigned to this doctor.")

print()

# ── Step 3: Get All Patients Under This Doctor ────────────────
print(f"Fetching patients assigned to {full_name}...")

all_patients = []
offset = 0
while True:
    r = requests.get(f"{BASE_URL}/patients", headers=headers, params={
        "departmentid": DEPARTMENT_ID,
        "providerid":   provider_id,
        "limit":        100,
        "offset":       offset,
    })
    data = r.json()
    batch = data.get("patients", [])
    all_patients.extend(batch)
    offset += 100
    if offset >= data.get("totalcount", 0):
        break

print(f"  Total patients: {len(all_patients)}\n")

# ── Step 4: Clinical Chart Task Inbox (Per Patient) ───────────
print(f"Scanning clinical chart task inbox across {len(all_patients)} patient(s)...")
print("  (Only showing patients with active tasks)\n")

patients_with_tasks = []

for patient in all_patients:
    pid = patient["patientid"]
    r = requests.get(
        f"{BASE_URL}/providers/{provider_id}/inbox",
        headers=headers,
        params={"departmentid": DEPARTMENT_ID, "patientid": pid}
    )
    result = r.json()
    task_count = result.get("totalcount", 0)

    if task_count > 0:
        patients_with_tasks.append({
            "patient":  patient,
            "tasks":    result.get("tasks", []),
            "count":    task_count,
        })

if patients_with_tasks:
    print(f"  Found {len(patients_with_tasks)} patient(s) with pending tasks:\n")
    for entry in patients_with_tasks:
        p = entry["patient"]
        print(f"  Patient: {p.get('firstname','')} {p.get('lastname','')} (ID: {p['patientid']})")
        for task in entry["tasks"]:
            print(f"    - [{task.get('tasktype','Task')}] {task.get('tasknote','No note')} | due: {task.get('duedate','N/A')}")
        print()
else:
    print("  No pending clinical tasks found for any patient.\n")

# ── Summary ───────────────────────────────────────────────────
print("=" * 55)
print(f"  Inbox Summary for {full_name}")
print("=" * 55)
print(f"  Admin documents (referrals/faxes): {total_admin}")
print(f"  Total patients:                    {len(all_patients)}")
print(f"  Patients with clinical tasks:      {len(patients_with_tasks)}")
print("=" * 55)
