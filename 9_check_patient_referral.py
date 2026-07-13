# STEP 9 — Verify the referral document is now linked to the patient in AthenaHealth.
# Queries the patient's admin documents list. Update PATIENT_ID to match Step 6.

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

response = requests.get(
    f"{BASE_URL}/patients/{PATIENT_ID}/documents/admin",
    headers=headers,
    params={
        "departmentid": "144",
    }
)

print("STATUS:", response.status_code)
print(json.dumps(response.json(), indent=2))