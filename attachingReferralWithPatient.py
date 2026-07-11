import requests
import json
import io
from PIL import Image
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

# Download PNG from unmatched document
print("Downloading fax image...")
page_url = "https://api.preview.platform.athenahealth.com/v1/195900/documents/admin/239639/pages/83679"
image_bytes = requests.get(page_url, headers=headers).content
print(f"PNG size: {len(image_bytes)} bytes")

# Convert PNG to JPEG
png_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
jpeg_buffer = io.BytesIO()
png_image.save(jpeg_buffer, format="JPEG", quality=95)
jpeg_buffer.seek(0)
print(f"JPEG size: {jpeg_buffer.getbuffer().nbytes} bytes")

# Upload to patient chart
print(f"Uploading to patient {PATIENT_ID}...")
response = requests.post(
    f"{BASE_URL}/patients/{PATIENT_ID}/documents/admin",
    headers=headers,
    files={"attachmentcontents": ("referral.jpg", jpeg_buffer, "image/jpeg")},
    data={
        "departmentid":     "144",
        "documentsubclass": "REFERRAL",
        "internalnote":     "Referral processed by automation. Patient registered.",
        "documentroute":    "FAX",
        "status":           "CLOSED",
    }
)

print("STATUS:", response.status_code)
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    new_admin_id = response.json().get("adminid")
    print(f"\nReferral attached to patient {PATIENT_ID}. New adminid: {new_admin_id}")