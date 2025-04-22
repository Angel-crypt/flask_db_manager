import os
import requests
from dotenv import load_dotenv
load_dotenv()

DB_MS_URL = os.getenv("DB_MS_URL")
API_KEY = os.getenv("DB_MS_API_KEY")
HEADERS = {"X-API-KEY": API_KEY}


class DBClient:
    @classmethod
    def create_user(cls, payload: dict) -> int:
        r = requests.post(f"{DB_MS_URL}/users", json=payload, headers=HEADERS)
        r.raise_for_status()
        return r.json()["user_id"]

    @classmethod
    def get_user_by_email(cls, email: str) -> dict:
        r = requests.get(f"{DB_MS_URL}/users/by-email",
                         params={"email": email}, headers=HEADERS)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    @classmethod
    def get_user_by_id(cls, user_id: int) -> dict:
        r = requests.get(f"{DB_MS_URL}/users/{user_id}", headers=HEADERS)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
