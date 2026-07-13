import requests
from . import config


def find_existing_patient(headers: dict, firstname: str, lastname: str, dob: str) -> str:
    r = requests.get(f"{config.BASE_URL}/patients", headers=headers, params={
        "departmentid": config.DEPARTMENT_ID,
        "firstname":    firstname,
        "lastname":     lastname,
        "dob":          dob,
    })
    if r.status_code != 200:
        return None
    patients = r.json().get("patients", [])
    if patients:
        return str(patients[0]["patientid"])
    return None


def register_patient(headers: dict, extraction) -> str:
    p = extraction.patient
    g = extraction.guarantor

    payload = {
        "firstname":                      p.firstname,
        "lastname":                       p.lastname,
        "dob":                            p.dob,
        "sex":                            p.sex,
        "departmentid":                   config.DEPARTMENT_ID,
        "mobilephone":                    p.mobilephone,
        "homephone":                      p.homephone,
        "email":                          p.email,
        "address1":                       p.address1,
        "city":                           p.city,
        "state":                          p.state,
        "zip":                            p.zip,
        "guarantorfirstname":             g.guarantorfirstname,
        "guarantorlastname":              g.guarantorlastname,
        "guarantordob":                   g.guarantordob,
        "guarantorrelationshiptopatient": g.guarantorrelationshiptopatient,
    }
    # AthenaHealth rejects null values for optional fields
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(f"{config.BASE_URL}/patients", headers=headers, data=payload)
    if r.status_code != 200:
        raise Exception(f"Patient registration failed ({r.status_code}): {r.text}")

    return str(r.json()[0]["patientid"])
