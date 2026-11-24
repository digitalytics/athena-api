import requests

CLIENT_ID     = "0oa13c168ol93YVOl298"
CLIENT_SECRET = "R0XHO8EbeUD8v69T9tWc3X0b5XjRIWLwF2kGe0kpfTK-PL5YPOpgBGOP_AAMKqS2"
PRACTICE_ID   = "195900"
DEPARTMENT_ID = "144"
BASE_URL      = f"https://api.preview.platform.athenahealth.com/v1/{PRACTICE_ID}"

token = requests.post(
    "https://api.preview.platform.athenahealth.com/oauth2/v1/token",
    data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
    auth=(CLIENT_ID, CLIENT_SECRET)
).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

all_providers = []
offset = 0

while True:
    r = requests.get(f"{BASE_URL}/providers", headers=headers, params={
        "departmentid": DEPARTMENT_ID,
        "limit":        100,
        "offset":       offset,
    })
    data = r.json()
    batch = data.get("providers", [])
    all_providers.extend(batch)
    offset += 100
    if offset >= data.get("totalcount", 0):
        break

doctors = sorted(all_providers, key=lambda p: p.get("providerid", 0))

print(f"{'ID':<8} {'Name':<30} {'Specialty':<35} {'Username':<20} {'NPI':<15} {'Billable'}")
print("-" * 125)
for d in doctors:
    name = f"{d.get('firstname','')} {d.get('lastname','')}".strip()
    print(
        f"{d['providerid']:<8} "
        f"{name:<30} "
        f"{d.get('specialty', 'N/A'):<35} "
        f"{d.get('providerusername', 'N/A'):<20} "
        f"{d.get('npi', 'N/A'):<15} "
        f"{'Yes' if d.get('billable') else 'No'}"
    )

print(f"\nTotal providers: {len(doctors)}")
