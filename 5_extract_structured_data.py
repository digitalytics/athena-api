# STEP 5 — Parse the OCR text into structured JSON using OpenAI (GPT-4o-mini).
# Reads referral_extracted.txt (from Step 4), extracts patient/insurance/provider fields,
# and saves the result to referral_structured.json for use in the next steps.

import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Pydantic Models ───────────────────────────────────────────

class PatientInfo(BaseModel):
    firstname: str = Field(description="Patient first name")
    lastname: str = Field(description="Patient last name")
    dob: str = Field(description="Date of birth in MM/DD/YYYY format")
    sex: str = Field(description="Sex - must be M or F only")
    mobilephone: Optional[str] = Field(default=None, description="Mobile phone number digits only")
    homephone: Optional[str] = Field(default=None, description="Home phone number digits only")
    email: Optional[str] = Field(default=None, description="Email address")
    address1: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="2-letter state code")
    zip: Optional[str] = Field(default=None, description="ZIP code")

class GuarantorInfo(BaseModel):
    guarantorfirstname: Optional[str] = Field(default=None, description="Guarantor first name")
    guarantorlastname: Optional[str] = Field(default=None, description="Guarantor last name")
    guarantordob: Optional[str] = Field(default=None, description="Guarantor DOB in MM/DD/YYYY")
    guarantorrelationshiptopatient: Optional[str] = Field(default=None, description="1=Self 2=Spouse 3=Child 4=Other")

class ReferringProvider(BaseModel):
    name: Optional[str] = Field(default=None, description="Referring provider full name")
    npi: Optional[str] = Field(default=None, description="Provider NPI number")
    practice: Optional[str] = Field(default=None, description="Practice or clinic name")
    phone: Optional[str] = Field(default=None, description="Provider phone")
    fax: Optional[str] = Field(default=None, description="Provider fax")

class InsuranceInfo(BaseModel):
    payer: Optional[str] = Field(default=None, description="Insurance payer name")
    plan_type: Optional[str] = Field(default=None, description="Plan type e.g. PPO HMO")
    policy_number: Optional[str] = Field(default=None, description="Policy number")
    group_id: Optional[str] = Field(default=None, description="Group ID")
    policy_holder: Optional[str] = Field(default=None, description="Policy holder name")

class ReferralDetails(BaseModel):
    referred_to: Optional[str] = Field(default=None, description="Specialty or department referred to")
    reason: Optional[str] = Field(default=None, description="Reason for referral")
    primary_diagnosis: Optional[str] = Field(default=None, description="Primary diagnosis with ICD-10 code")
    secondary_diagnosis: Optional[str] = Field(default=None, description="Secondary diagnosis if any")
    urgency: Optional[str] = Field(default=None, description="Urgency level")
    auth_number: Optional[str] = Field(default=None, description="Authorization number")
    clinical_notes: Optional[str] = Field(default=None, description="Clinical notes or additional info")

class ReferralExtraction(BaseModel):
    patient: PatientInfo
    guarantor: GuarantorInfo
    referring_provider: ReferringProvider
    insurance: InsuranceInfo
    referral: ReferralDetails

# ── Load extracted text ───────────────────────────────────────

with open("referral_extracted.txt", "r", encoding="utf-8") as f:
    extracted_text = f.read()

print("Text loaded. Sending to OpenAI for structured extraction...")

# ── Stage 2: Structured Extraction ───────────────────────────

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a medical data extraction specialist. "
                "Extract all patient, referral, insurance, and provider information "
                "from the referral document text. "
                "For phone numbers return digits only, no dashes or brackets. "
                "For sex return only M or F. "
                "For dates use MM/DD/YYYY format. "
                "If a field is not found, return null."
            )
        },
        {
            "role": "user",
            "content": f"Extract all information from this referral document:\n\n{extracted_text}"
        }
    ],
    response_format=ReferralExtraction
)

result = response.choices[0].message.parsed

print("\n========== EXTRACTED STRUCTURED DATA ==========")
print(json.dumps(result.model_dump(), indent=2))

# Save to JSON
with open("referral_structured.json", "w", encoding="utf-8") as f:
    json.dump(result.model_dump(), f, indent=2)

print("\nSaved to referral_structured.json")

# Preview patient registration fields
print("\n========== PATIENT REGISTRATION FIELDS ==========")
print(f"First Name:  {result.patient.firstname}")
print(f"Last Name:   {result.patient.lastname}")
print(f"DOB:         {result.patient.dob}")
print(f"Sex:         {result.patient.sex}")
print(f"Mobile:      {result.patient.mobilephone}")
print(f"Address:     {result.patient.address1}, {result.patient.city}, {result.patient.state} {result.patient.zip}")