import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID   = "195900"
DEPARTMENT_ID = "144"
BASE_URL      = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"
TOKEN_URL     = "https://api.preview.platform.athenahealth.com/oauth2/v1/token"
SCOPE         = "athena/service/Athenanet.MDP.*"

INBOX_START   = "01/01/2020"
INBOX_END     = "12/31/2026"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set one of these to target a doctor. PROVIDER_ID takes precedence if both set.
TARGET_DOCTOR_NAME = "Alcatraz"
TARGET_PROVIDER_ID = None          # e.g. 2360

ADMIN_REFERRAL_SUBCLASS = "ADMIN_REFERRAL"
