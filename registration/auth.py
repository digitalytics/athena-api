import requests
from . import config


def get_token() -> str:
    response = requests.post(
        config.TOKEN_URL,
        data={"grant_type": "client_credentials", "scope": config.SCOPE},
        auth=(config.CLIENT_ID, config.CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]
