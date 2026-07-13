import io
import requests
from PIL import Image
from . import config


def attach_referral_to_patient(headers: dict, patient_id: str, pages: list) -> str:
    new_admin_id = None
    for i, page in enumerate(pages, start=1):
        image_bytes = requests.get(page["href"], headers=headers).content

        png_image   = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        jpeg_buffer = io.BytesIO()
        png_image.save(jpeg_buffer, format="JPEG", quality=95)
        jpeg_buffer.seek(0)

        r = requests.post(
            f"{config.BASE_URL}/patients/{patient_id}/documents/admin",
            headers=headers,
            files={"attachmentcontents": (f"referral_page{i}.jpg", jpeg_buffer, "image/jpeg")},
            data={
                "departmentid":     config.DEPARTMENT_ID,
                "documentsubclass": "REFERRAL",
                "documentroute":    "FAX",
                "status":           "CLOSED",
                "internalnote":     f"Referral processed by automation. Page {i} of {len(pages)}.",
            },
        )
        if r.status_code != 200:
            raise Exception(f"Attach referral failed (page {i}, status {r.status_code}): {r.text}")

        new_admin_id = r.json().get("adminid")

    return str(new_admin_id)


def close_inbox_document(headers: dict, admin_id: int) -> bool:
    r = requests.put(
        f"{config.BASE_URL}/documents/admin/{admin_id}",
        headers=headers,
        data={"status": "CLOSED"},
    )
    return r.status_code == 200
