from helpers import mygoogler
from django.utils import timezone
from .models import Contact
import socket


def sync_google_other_contacts(user, max_results=2):
    print("🔍 Step 1: Starting sync_google_other_contacts")

    page_token = None
    break_full_sync = False
    total_complete = 0
    page_count = 0
    max_pages = 5  # Safety limit to prevent infinite loops

    # Set timeout for Google API calls
    socket.setdefaulttimeout(30)  # 30 second timeout

    while True and page_count < max_pages:
        page_count += 1
        print(f"🔍 Step 2: Processing page {page_count}...")

        try:
            print("🔍 Step 2a: Calling Google API...")
            results = mygoogler.get_my_other_contacts(user, page_token=page_token)

            if not results:
                print("❌ No results from Google API")
                break

            print(
                f"🔍 Step 2b: Google API returned {len(results.get('otherContacts', []))} contacts"
            )

        except socket.timeout:
            print("❌ Google API request timed out after 30 seconds")
            break
        except Exception as e:
            print(f"❌ Google API error: {e}")
            break

        print("🔍 Step 3: Parsing contact info...")
        # FIX: Changed from parse_contact_info to parse_contact_infor
        parsed_results = mygoogler.parse_contact_infor(results)
        print(f"🔍 Step 4: Parsed {len(parsed_results)} contacts")

        page_token = results.get("nextPageToken")
        print(f"🔍 Step 5: Next page token: {page_token}")

        print("🔍 Step 6: Processing contacts...")
        for i, contact_data in enumerate(parsed_results):
            email = contact_data.get("email")
            print(f"   Processing contact {i+1}: {email}")

            try:
                Contact.objects.update_or_create(
                    user=user,
                    email=email,
                    defaults={
                        "first_name": contact_data.get("first_name") or "",
                        "last_name": contact_data.get("last_name") or "",
                        "last_sync": timezone.now(),
                    },
                )
                print(f"   ✅ Saved: {email}")

            except Exception as e:
                print(f"   ❌ Error saving {email}: {e}")

            total_complete += 1
            print(f"   Total completed: {total_complete}/{max_results}")

            if total_complete >= max_results:
                print("🔍 Reached max results limit")
                break_full_sync = True
                break

        if break_full_sync:
            print("🔍 Breaking out of sync loop (max results reached)")
            break

        if not page_token:
            print("🔍 No more pages to process")
            break

        if page_count >= max_pages:
            print("⚠️ Reached maximum page limit for safety")
            break

    print(
        f"✅ Sync completed! Processed {total_complete} contacts across {page_count} pages"
    )
    return total_complete
