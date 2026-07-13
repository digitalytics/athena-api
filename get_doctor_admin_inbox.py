# Replicates the "Admin / Phone Messages" inbox view from the AthenaHealth portal
# for a specific doctor. Shows patient info, status, description, department,
# created/updated dates, and time in inbox — matching the portal layout.

import requests
import json
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────
CLIENT_ID     = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID   = "195900"
DEPARTMENT_ID = "144"
BASE_URL      = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

# ── Set your doctor here ──────────────────────────────────────
SEARCH_NAME = "Alcatraz"   # partial last name  (set None to use PROVIDER_ID)
PROVIDER_ID = None         # or use a known ID directly e.g. 2360

INBOX_START = "01/01/2020"
INBOX_END   = "12/31/2026"

# Admin / Phone Messages covers these subclasses (mirrors what the portal groups together)
ADMIN_SUBCLASSES = [
    "ADMIN_REFERRAL",
    "ADMIN_PHONEENCOUNTER",
    "ADMIN_LETTER",
    "ADMIN_TASK",
    "ADMIN_PATIENTCASE",
]

# ── Auth ──────────────────────────────────────────────────────
token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET)
).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# ── Find the doctor ───────────────────────────────────────────
def find_provider(name=None, provider_id=None):
    if provider_id:
        return requests.get(f"{BASE_URL}/providers/{provider_id}", headers=headers).json()[0]
    offset = 0
    while True:
        data = requests.get(f"{BASE_URL}/providers", headers=headers, params={
            "departmentid": DEPARTMENT_ID, "limit": 100, "offset": offset
        }).json()
        for p in data.get("providers", []):
            full = f"{p.get('firstname','')} {p.get('lastname','')}".lower()
            if name.lower() in full:
                return p
        offset += 100
        if offset >= data.get("totalcount", 0):
            break
    return None

provider = find_provider(name=SEARCH_NAME, provider_id=PROVIDER_ID)
if not provider:
    print("Doctor not found.")
    exit(1)

scheduling_name = provider.get("schedulingname", "")
full_name       = f"{provider.get('firstname','')} {provider.get('lastname','')}".strip()
provider_id_val = provider["providerid"]

# ── Fetch all admin documents assigned to this doctor ─────────
all_docs = []

for subclass in ADMIN_SUBCLASSES:
    r = requests.get(f"{BASE_URL}/documents/admin", headers=headers, params={
        "departmentid":     DEPARTMENT_ID,
        "documentsubclass": subclass,
        "startdate":        INBOX_START,
        "enddate":          INBOX_END,
        "assignedto":       scheduling_name,
        "limit":            100,
    })
    if r.status_code == 200:
        docs = r.json().get("admins", [])
        for d in docs:
            d["_subclass_queried"] = subclass
        all_docs.extend(docs)

# ── Fetch patient details for each doc that has a patientid ──
patient_cache = {}

def get_patient(patient_id):
    if patient_id in patient_cache:
        return patient_cache[patient_id]
    r = requests.get(f"{BASE_URL}/patients/{patient_id}", headers=headers,
                     params={"departmentid": DEPARTMENT_ID})
    if r.status_code == 200:
        data = r.json()
        p = data[0] if isinstance(data, list) else data
        patient_cache[patient_id] = p
        return p
    return None

# ── Helpers ───────────────────────────────────────────────────
def age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%m/%d/%Y")
        return (datetime.now() - dob).days // 365
    except:
        return "?"

def time_in_inbox(created_str):
    try:
        created = datetime.fromisoformat(created_str)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - created
        days = delta.days
        if days == 0:
            return "Today"
        elif days == 1:
            return "1 day"
        else:
            return f"{days} days"
    except:
        return "N/A"

def format_description(doc):
    subclass = doc.get("documentsubclass", "")
    note     = doc.get("internalnote", "") or doc.get("description", "")
    label_map = {
        "ADMIN_REFERRAL":      "Admin - Referral",
        "ADMIN_PHONEENCOUNTER":"Admin - Phone",
        "ADMIN_LETTER":        "Admin - Letter",
        "ADMIN_TASK":          "Admin - Task",
        "ADMIN_PATIENTCASE":   "Admin - Patient Case",
    }
    label = label_map.get(subclass, "Admin")
    if note:
        return f"{label} | {note}"
    return label

def format_date(dt_str):
    try:
        return datetime.fromisoformat(dt_str).strftime("%m-%d-%Y")
    except:
        return dt_str[:10] if dt_str else "N/A"

# ── Build inbox rows ──────────────────────────────────────────
rows = []
for doc in all_docs:
    patient_id  = doc.get("patientid")
    patient_str = "Unassigned"
    dob_str     = ""
    sex_str     = ""

    if patient_id:
        p = get_patient(str(patient_id))
        if p:
            name    = f"{p.get('lastname','')}, {p.get('firstname','')}".strip(", ")
            dob_str = p.get("dob", "")
            sex_str = p.get("sex", "")
            a       = age(dob_str)
            patient_str = f"{name}\n  {a}{'F' if sex_str=='F' else 'M'} | {dob_str} | #{patient_id}"

    rows.append({
        "patient":      patient_str,
        "status":       doc.get("status", ""),
        "description":  format_description(doc),
        "department":   doc.get("departmentid", ""),
        "created":      format_date(doc.get("createddatetime", "")),
        "last_updated": format_date(doc.get("lastmodifieddatetime", "")),
        "time_inbox":   time_in_inbox(doc.get("createddatetime", "")),
        "adminid":      doc.get("adminid", ""),
    })

# Sort by created date descending (newest first)
rows.sort(key=lambda x: x["created"], reverse=True)

# ── Print inbox ───────────────────────────────────────────────
print(f"\n  {full_name}  >  Admin / Phone Messages  ({len(rows)} tasks)")
print("=" * 115)
print(f"  {'Patient':<35} {'Status':<10} {'Description':<40} {'Dept':<6} {'Created':<12} {'Last Updated':<12} {'In Inbox'}")
print(f"  {'-'*34:<35} {'-'*9:<10} {'-'*39:<40} {'-'*5:<6} {'-'*11:<12} {'-'*11:<12} {'-'*8}")

if not rows:
    print("\n  No items found in Admin / Phone Messages inbox.")
else:
    for i, (row, doc) in enumerate(zip(rows, sorted(all_docs, key=lambda d: d.get("createddatetime",""), reverse=True))):
        print(f"\n  --- Row {i+1} ---------------------------------------------------")
        # Formatted row
        patient_lines = row["patient"].split("\n")
        print(
            f"  {patient_lines[0]:<35} "
            f"{row['status']:<10} "
            f"{row['description'][:38]:<40} "
            f"{row['department']:<6} "
            f"{row['created']:<12} "
            f"{row['last_updated']:<12} "
            f"{row['time_inbox']}"
        )
        if len(patient_lines) > 1:
            print(f"  {patient_lines[1]:<35}")
        # Raw API response
        print(f"\n  Raw API response:")
        print(json.dumps(doc, indent=4))

print("=" * 115)
print(f"  Total: {len(rows)} item(s) in Admin / Phone Messages")
print()
