import requests
from . import config


def list_all_doctors(headers: dict) -> list:
    doctors = []
    offset = 0
    while True:
        r = requests.get(f"{config.BASE_URL}/providers", headers=headers, params={
            "departmentid": config.DEPARTMENT_ID,
            "limit":        100,
            "offset":       offset,
        })
        r.raise_for_status()
        data = r.json()
        batch = data.get("providers", [])
        doctors.extend([p for p in batch if p.get("providertype") == "MD" and p.get("billable")])
        offset += 100
        if offset >= data.get("totalcount", 0):
            break
    return doctors


def find_provider(headers: dict, name: str = None, provider_id: int = None) -> dict:
    if provider_id:
        r = requests.get(f"{config.BASE_URL}/providers/{provider_id}", headers=headers)
        r.raise_for_status()
        return r.json()[0]

    offset = 0
    while True:
        r = requests.get(f"{config.BASE_URL}/providers", headers=headers, params={
            "departmentid": config.DEPARTMENT_ID,
            "limit":        100,
            "offset":       offset,
        })
        r.raise_for_status()
        data = r.json()
        for p in data.get("providers", []):
            full = f"{p.get('firstname', '')} {p.get('lastname', '')}".lower()
            if name.lower() in full:
                return p
        offset += 100
        if offset >= data.get("totalcount", 0):
            break
    return None
