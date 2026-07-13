import logging
import requests
from . import config

logger = logging.getLogger(__name__)


def _find_insurance_package_id(headers: dict, payer_name: str) -> str:
    r = requests.get(f"{config.BASE_URL}/insurancepackages", headers=headers, params={
        "insuranceplanname": payer_name,
        "departmentid":      config.DEPARTMENT_ID,
    })
    if r.status_code != 200:
        return None
    packages = r.json().get("insurancepackages", [])
    if packages:
        return str(packages[0].get("insurancepackageid"))
    return None


def post_insurance(headers: dict, patient_id: str, insurance) -> dict:
    if not insurance.payer:
        logger.warning(f"patient={patient_id} | insurance skipped — no payer name extracted")
        return {}

    package_id = _find_insurance_package_id(headers, insurance.payer)
    if not package_id:
        logger.warning(f"patient={patient_id} | insurance skipped — package ID not found for '{insurance.payer}'")
        return {}

    payload = {
        "departmentid":        config.DEPARTMENT_ID,
        "insurancepackageid":  package_id,
        "sequencenumber":      "1",
        "insurancepolicyholder": insurance.policy_holder or "SELF",
    }
    if insurance.policy_number:
        payload["policynumber"] = insurance.policy_number
    if insurance.group_id:
        payload["groupid"] = insurance.group_id

    r = requests.post(
        f"{config.BASE_URL}/patients/{patient_id}/insurances",
        headers=headers,
        data=payload,
    )
    if r.status_code != 200:
        logger.warning(f"patient={patient_id} | insurance POST failed ({r.status_code}): {r.text[:200]}")
        return {}

    logger.info(f"patient={patient_id} | insurance posted: {insurance.payer}")
    return r.json()
