# STEP 6 — Register the patient in AthenaHealth using data from referral_structured.json (Step 5).
# Posts to the AthenaHealth patients endpoint and saves the returned patientid
# back into referral_structured.json for use in subsequent steps.

import requests
import json
import os
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

# Load extracted data
with open("referral_structured.json", "r") as f:
    data = json.load(f)

p = data["patient"]
g = data["guarantor"]

# Build patient registration payload
payload = {
    # Required
    "firstname":                     p["firstname"],
    "lastname":                      p["lastname"],
    "dob":                           p["dob"],
    "sex":                           p["sex"],
    "departmentid":                  "144",

    # Optional patient fields
    "mobilephone":                   p["mobilephone"],
    "homephone":                     p["homephone"],
    "email":                         p["email"],
    "address1":                      p["address1"],
    "city":                          p["city"],
    "state":                         p["state"],
    "zip":                           p["zip"],

    # Guarantor
    "guarantorfirstname":            g["guarantorfirstname"],
    "guarantorlastname":             g["guarantorlastname"],
    "guarantordob":                  g["guarantordob"],
    "guarantorrelationshiptopatient": g["guarantorrelationshiptopatient"],
}

print("Registering patient...")
print(json.dumps(payload, indent=2))

response = requests.post(
    f"{BASE_URL}/patients",
    headers=headers,
    data=payload
)

print("\nSTATUS:", response.status_code)
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    patient_id = response.json()[0]["patientid"]
    print(f"\nPatient registered. Patient ID: {patient_id}")

    # Save patient ID for next step
    with open("referral_structured.json", "r") as f:
        full_data = json.load(f)

    full_data["athena_patient_id"] = patient_id

    with open("referral_structured.json", "w") as f:
        json.dump(full_data, f, indent=2)

    print("Patient ID saved to referral_structured.json")