import requests
from . import config


def get_unmatched_referrals(headers: dict, scheduling_name: str) -> list:
    r = requests.get(f"{config.BASE_URL}/documents/admin", headers=headers, params={
        "departmentid":     config.DEPARTMENT_ID,
        "documentsubclass": config.ADMIN_REFERRAL_SUBCLASS,
        "startdate":        config.INBOX_START,
        "enddate":          config.INBOX_END,
        "assignedto":       scheduling_name,
        "limit":            100,
    })
    r.raise_for_status()
    docs = r.json().get("admins", [])
    # Only return referrals not yet matched to a patient
    return [doc for doc in docs if not doc.get("patientid")]


def get_admin_doc_detail(headers: dict, admin_id: int) -> dict:
    r = requests.get(f"{config.BASE_URL}/documents/admin/{admin_id}", headers=headers)
    r.raise_for_status()
    data = r.json()
    return data[0] if isinstance(data, list) else data
