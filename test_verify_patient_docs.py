# TEST/DEBUG — Multi-check verification script: fetches a document record, checks patient admin docs
# with CLOSED status, and checks patient docs without a filter. Used to debug whether a referral
# was successfully attached to a patient. Not part of the main pipeline.

import requests
import json
from dotenv import load_dotenv

load_dotenv()

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

PATIENT_ID = "68400"
ADMIN_ID   = "239639"

# Check 1 — fetch the document directly and see if patientid is on it now
print("--- CHECK 1: Document record ---")
doc = requests.get(
    f"{BASE_URL}/documents/admin/{ADMIN_ID}",
    headers=headers
).json()
print(json.dumps(doc, indent=2))

# Check 2 — patient documents with all statuses
print("\n--- CHECK 2: Patient docs all statuses ---")
r2 = requests.get(
    f"{BASE_URL}/patients/{PATIENT_ID}/documents/admin",
    headers=headers,
    params={
        "departmentid": "144",
        "status":       "CLOSED",
    }
)
print(json.dumps(r2.json(), indent=2))

# Check 3 — without any status filter
print("\n--- CHECK 3: Patient docs no filter ---")
r3 = requests.get(
    f"{BASE_URL}/patients/{PATIENT_ID}/documents",
    headers=headers,
    params={"departmentid": "144"}
)
print("Status:", r3.status_code)
print(json.dumps(r3.json(), indent=2))