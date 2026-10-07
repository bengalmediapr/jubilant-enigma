"""Find local Puerto Rico businesses with the Google Places API (New).

Apollo is built for B2B/SaaS contacts and has thin coverage of the restaurants,
clinics, contractors and shops that buy websites in Puerto Rico. Google Maps
listings are the better lead source here: every listing tells us whether the
business has a website at all, and businesses without one are the warmest leads.
"""

import os
import time

import requests

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.websiteUri",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.rating",
        "places.userRatingCount",
        "places.googleMapsUri",
        "places.primaryTypeDisplayName",
        "places.businessStatus",
        "nextPageToken",
    ]
)

# Social profiles that some businesses list as their "website".
SOCIAL_HOSTS = ("facebook.com", "instagram.com", "linktr.ee", "wa.me", "tiktok.com")


def search(category: str, municipio: str, max_pages: int = 3) -> list[dict]:
    """Return businesses matching e.g. ("restaurantes", "Ponce")."""
    key = os.environ["GOOGLE_PLACES_API_KEY"]
    headers = {"X-Goog-Api-Key": key, "X-Goog-FieldMask": FIELDS}
    body = {
        "textQuery": f"{category} en {municipio}, Puerto Rico",
        "languageCode": "es",
        "regionCode": "PR",
        "pageSize": 20,
    }
    leads = []
    for _ in range(max_pages):
        resp = requests.post(SEARCH_URL, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for place in data.get("places", []):
            if place.get("businessStatus", "OPERATIONAL") != "OPERATIONAL":
                continue
            leads.append(_to_lead(place, category, municipio))
        token = data.get("nextPageToken")
        if not token:
            break
        body["pageToken"] = token
        time.sleep(2)  # next page token takes a moment to become valid
    return leads


def _to_lead(place: dict, category: str, municipio: str) -> dict:
    website = place.get("websiteUri", "") or ""
    if not website:
        website_status = "none"
    elif any(host in website.lower() for host in SOCIAL_HOSTS):
        website_status = "social_only"
    else:
        website_status = "has_site"
    return {
        "place_id": place.get("id", ""),
        "name": place.get("displayName", {}).get("text", ""),
        "category": category,
        "type": place.get("primaryTypeDisplayName", {}).get("text", ""),
        "municipio": municipio,
        "address": place.get("formattedAddress", ""),
        "phone": place.get("nationalPhoneNumber", ""),
        "phone_intl": place.get("internationalPhoneNumber", ""),
        "website": website,
        "website_status": website_status,
        "rating": place.get("rating", ""),
        "reviews": place.get("userRatingCount", 0),
        "maps_url": place.get("googleMapsUri", ""),
    }
