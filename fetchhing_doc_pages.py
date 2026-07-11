import requests
import os

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

# Latest referral — adminid 239631, pageid 83677
page_url = "https://api.preview.platform.athenahealth.com/v1/195900/documents/admin/239639/pages/83679"

response = requests.get(page_url, headers=headers)

print("STATUS:", response.status_code)
print("CONTENT TYPE:", response.headers.get("content-type"))
print("FILE SIZE:", len(response.content), "bytes")

with open("referral_sarah.png", "wb") as f:
    f.write(response.content)

print("Saved as referral_sarah.png")
os.startfile(os.path.abspath("referral_sarah.png"))