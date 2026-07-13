import base64
import requests
from openai import OpenAI
from . import config

_client = OpenAI(api_key=config.OPENAI_API_KEY)


def ocr_referral_pages(headers: dict, pages: list) -> str:
    full_text = ""
    for page in pages:
        image_bytes = requests.get(page["href"], headers=headers).content
        image_b64   = base64.b64encode(image_bytes).decode("utf-8")

        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Transcribe all text from this referral document exactly as it appears. "
                            "Include every label, value, and field. Do not summarize."
                        ),
                    },
                ],
            }],
            max_tokens=2000,
        )
        full_text += f"\n--- Page {page['pageid']} ---\n{response.choices[0].message.content}"

    return full_text
