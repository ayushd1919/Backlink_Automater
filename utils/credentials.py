# utils/credentials.py
import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from config import CREDENTIALS_FILE  # already used in your project

@dataclass
class SiteCreds:
    username: Optional[str]
    email: Optional[str]
    password: str
    profile_url: Optional[str] = None

def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Credentials file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_site_credentials(site_key: str) -> SiteCreds:
    """
    Look up credentials by site key. Accepts common variants like 'FreelistingUK',
    'FreeListingUK', 'Free Listing UK'.
    """
    data = _load_json(CREDENTIALS_FILE)
    # Build candidate keys (case-insensitive, whitespace-agnostic)
    norm = site_key.replace(" ", "").lower()
    candidates = [
        site_key,
        site_key.replace(" ", ""),
        site_key.replace(" ", "_"),
        site_key.title(),
        "FreeListing UK",  # common canonical
        "Freelisting UK",
        "freelisting uk",
    ]
    block = None
    for k in candidates:
        if k in data:
            block = data[k]
            break
    if not block:
        # last try: case-insensitive scan
        for k, v in data.items():
            if k.replace(" ", "").lower() == norm:
                block = v
                break
    if not block:
        raise KeyError(f"No credentials found for site: {site_key}")

    username = block.get("username")
    email = block.get("email")
    password = block.get("password")
    profile_url = block.get("profile_url")
    if not password or not (email or username):
        raise ValueError(f"Incomplete credentials for {site_key}. Need password AND (email or username).")

    return SiteCreds(username=username, email=email, password=password, profile_url=profile_url)
