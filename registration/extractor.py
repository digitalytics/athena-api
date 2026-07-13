from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from . import config

_client = OpenAI(api_key=config.OPENAI_API_KEY)


class PatientInfo(BaseModel):
    firstname:   str            = Field(description="Patient first name")
    lastname:    str            = Field(description="Patient last name")
    dob:         str            = Field(description="Date of birth in MM/DD/YYYY format")
    sex:         str            = Field(description="Sex - must be M or F only")
    mobilephone: Optional[str]  = Field(default=None, description="Mobile phone digits only")
    homephone:   Optional[str]  = Field(default=None, description="Home phone digits only")
    email:       Optional[str]  = Field(default=None, description="Email address")
    address1:    Optional[str]  = Field(default=None, description="Street address")
    city:        Optional[str]  = Field(default=None, description="City")
    state:       Optional[str]  = Field(default=None, description="2-letter state code")
    zip:         Optional[str]  = Field(default=None, description="ZIP code")


class GuarantorInfo(BaseModel):
    guarantorfirstname:              Optional[str] = Field(default=None)
    guarantorlastname:               Optional[str] = Field(default=None)
    guarantordob:                    Optional[str] = Field(default=None, description="MM/DD/YYYY")
    guarantorrelationshiptopatient:  Optional[str] = Field(default=None, description="1=Self 2=Spouse 3=Child 4=Other")


class ReferringProvider(BaseModel):
    name:     Optional[str] = Field(default=None, description="Full name")
    npi:      Optional[str] = Field(default=None)
    practice: Optional[str] = Field(default=None)
    phone:    Optional[str] = Field(default=None)
    fax:      Optional[str] = Field(default=None)


class InsuranceInfo(BaseModel):
    payer:         Optional[str] = Field(default=None, description="Insurance payer name")
    plan_type:     Optional[str] = Field(default=None, description="e.g. PPO HMO")
    policy_number: Optional[str] = Field(default=None)
    group_id:      Optional[str] = Field(default=None)
    policy_holder: Optional[str] = Field(default=None)


class ReferralDetails(BaseModel):
    referred_to:         Optional[str] = Field(default=None, description="Specialty or department")
    reason:              Optional[str] = Field(default=None)
    primary_diagnosis:   Optional[str] = Field(default=None, description="With ICD-10 code")
    secondary_diagnosis: Optional[str] = Field(default=None)
    urgency:             Optional[str] = Field(default=None)
    auth_number:         Optional[str] = Field(default=None)
    clinical_notes:      Optional[str] = Field(default=None)


class ReferralExtraction(BaseModel):
    patient:            PatientInfo
    guarantor:          GuarantorInfo
    referring_provider: ReferringProvider
    insurance:          InsuranceInfo
    referral:           ReferralDetails


def extract_structured_data(ocr_text: str) -> ReferralExtraction:
    response = _client.beta.chat.completions.parse(
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
                ),
            },
            {
                "role": "user",
                "content": f"Extract all information from this referral document:\n\n{ocr_text}",
            },
        ],
        response_format=ReferralExtraction,
    )
    return response.choices[0].message.parsed
