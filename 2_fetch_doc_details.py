# STEP 2 — Fetch metadata/details of a specific admin document from AthenaHealth.
# Use this to confirm the uploaded referral document exists and see its status, pages, etc.
# Change the adminid (239639) to match the one returned in Step 1.

import requests
import json

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

doc = requests.get(
    f"{BASE_URL}/documents/admin/239639",
    headers=headers
).json()

print(json.dumps(doc, indent=2))