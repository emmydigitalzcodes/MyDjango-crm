from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings


def get_user_creds(user):
    try:
        got = user.google_oauth_token
    except:
        raise Exception("Google API not active for this user")
    data = {
        "token": got.access_token,
        "refresh_token": got.refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
    }
    return Credentials(**data)


def build_service(creds, service_name="people", version="v1"):
    return build(service_name, version, credentials=creds)


def get_my_contacts(user, page_token=None):
    import socket

    socket.setdefaulttimeout(30)

    creds = get_user_creds(user)
    service = build_service(creds, service_name="people", version="v1")

    try:
        results = (
            service.people()
            .connections()
            .list(
                pageSize=10,
                resourceName="people/me",
                personFields="names,emailAddresses",
                requestSyncToken=True,
                pageToken=page_token,
            )
            .execute()
        )
        return results
    except Exception as e:
        print(f"❌ Google Contacts API error: {e}")
        return None


def get_my_other_contacts(user, page_token=None):
    import socket

    socket.setdefaulttimeout(30)

    creds = get_user_creds(user)
    service = build_service(creds, service_name="people", version="v1")

    try:
        # Correct method - otherContacts is direct on service
        results = (
            service.otherContacts()  # ✅ FIXED: No .people() before it
            .list(
                pageSize=10,
                readMask="names,emailAddresses",
                requestSyncToken=True,
                pageToken=page_token,
            )
            .execute()
        )
        return results
    except Exception as e:
        print(f"❌ Google Other Contacts API error: {e}")
        return None


def parse_contact_infor(results):
    """
    Parse Google Contacts API results into a structured format
    """
    contacts = []
    if "connections" in results:
        items = results["connections"]
    elif "otherContacts" in results:
        items = results["otherContacts"]
    else:
        items = []

    for item in items:
        contact_data = {}

        # Parse names
        if "names" in item and item["names"]:
            contact_data["name"] = item["names"][0].get("displayName", "")
            # Split into first/last name if needed
            names = contact_data["name"].split(" ", 1)
            contact_data["first_name"] = names[0] if names else ""
            contact_data["last_name"] = names[1] if len(names) > 1 else ""

        # Parse emails
        if "emailAddresses" in item and item["emailAddresses"]:
            contact_data["email"] = item["emailAddresses"][0].get("value", "")

        # Parse phone numbers
        if "phoneNumbers" in item and item["phoneNumbers"]:
            contact_data["phone"] = item["phoneNumbers"][0].get("value", "")

        if contact_data.get("email"):  # Only add if we have email
            contacts.append(contact_data)

    return contacts
