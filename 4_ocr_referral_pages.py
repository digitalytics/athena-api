# STEP 4 — OCR the referral document pages using OpenAI Vision (GPT-4o-mini).
# Fetches all pages from the latest referral in the AthenaHealth inbox,
# sends each page image to OpenAI, and saves the full extracted text to referral_extracted.txt.

import requests
import base64
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CLIENT_ID = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID = "195900"
BASE_URL = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

# Get athena token
token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET)
).json()["access_token"]

athena_headers = {"Authorization": f"Bearer {token}"}

# Step 1 — get latest referral from inbox
inbox = requests.get(
    f"{BASE_URL}/documents/admin",
    headers=athena_headers,
    params={
        "departmentid":     "144",
        "documentsubclass": "ADMIN_REFERRAL",
        "startdate":        "01/01/2020",
        "enddate":          "12/31/2026",
        "limit":            10
    }
).json()

latest = sorted(inbox["admins"], key=lambda x: x["adminid"], reverse=True)[0]
admin_id = latest["adminid"]
print(f"Processing adminid: {admin_id}")

# Step 2 — get pages
doc = requests.get(
    f"{BASE_URL}/documents/admin/{admin_id}",
    headers=athena_headers
).json()[0]

pages = doc.get("pages", [])
print(f"Pages found: {len(pages)}")

# Step 3 — download each page and send to OpenAI vision
full_text = ""

for page in pages:
    image_bytes = requests.get(page["href"], headers=athena_headers).content
    image_b64   = base64.b64encode(image_bytes).decode("utf-8")

    print(f"Sending page {page['pageid']} to OpenAI...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Transcribe all text from this referral document exactly as it appears. Include every label, value, and field. Do not summarize."
                    }
                ]
            }
        ],
        max_tokens=2000
    )

    page_text = response.choices[0].message.content
    full_text += f"\n--- Page {page['pageid']} ---\n{page_text}"
    print(f"Extracted {len(page_text)} characters")

with open("referral_extracted.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("Saved to referral_extracted.txt")