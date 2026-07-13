# TEST/DEBUG — Download a single hardcoded referral page (adminid 239631, pageid 83677) as PNG.
# Opens the image automatically after saving. Used to visually inspect a referral page.
# Not part of the main pipeline — replaced by Step 3 (fetchhing_doc_pages.py).

import requests

CLIENT_ID = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID = "195900"
BASE_URL = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET)
).json()["access_token"]

# Download the page
response = requests.get(
    "https://api.preview.platform.athenahealth.com/v1/195900/documents/admin/239631/pages/83677",
    headers={"Authorization": f"Bearer {token}"}
)

with open("referral_download.png", "wb") as f:
    f.write(response.content)

print(f"Downloaded: {len(response.content)} bytes")
print("Saved as referral_download.png")

import os
os.startfile(os.path.abspath("referral_download.png"))