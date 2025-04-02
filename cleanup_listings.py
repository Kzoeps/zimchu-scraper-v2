import os
import requests
import datetime
from dotenv import load_dotenv
from supabase_zimchu import supabase
from datetime import datetime, timedelta


def is_facebook_listing_valid(post_url):
    """
    Check if a Facebook listing is still available.
    Returns True if the post still exists, False otherwise.
    """
    try:
        # Make a GET request to the Facebook post URL
        response = requests.get(post_url)

        # Check if the response status is successful (200)
        # AND ensure the content doesn't contain phrases showing the post is unavailable
        if (
            response.status_code == 200
            and "content isn't available" not in response.text.lower()
            and "this content isn't available" not in response.text.lower()
        ):
            return True
        return False
    except Exception as e:
        print(f"Error checking Facebook post {post_url}: {e}")
        # In case of error, better to be safe and assume the post might still be valid
        return True


def delete_invalid_facebook_listings():
    """
    Delete listings where the Facebook posts have been removed.
    """
    # Get all listings from Supabase
    response = supabase.table("listings_v2").select("id", "post_url").execute()

    # Track successfully deleted listings
    deleted_listings = []
    failed_listings = []

    print(f"Found {len(response.data)} listings to check for validity")

    for listing in response.data:
        listing_id = listing["id"]
        post_url = listing["post_url"]

        # Skip listings without a post URL
        if not post_url:
            continue

        print(f"Checking listing {listing_id} with URL {post_url}")

        # Check if the Facebook listing is still valid
        if not is_facebook_listing_valid(post_url):
            print(f"Listing {listing_id} no longer exists on Facebook, deleting...")

            try:
                # Delete the listing from Supabase
                delete_response = (
                    supabase.table("listings_v2")
                    .delete()
                    .eq("id", listing_id)
                    .execute()
                )
                deleted_listings.append(listing_id)
                print(f"Successfully deleted listing {listing_id}")
            except Exception as e:
                print(f"Failed to delete listing {listing_id}: {e}")
                failed_listings.append(listing_id)

    print(f"Deleted {len(deleted_listings)} invalid Facebook listings")
    if failed_listings:
        print(f"Failed to delete {len(failed_listings)} listings: {failed_listings}")

    return deleted_listings


def delete_old_listings(weeks=3):
    """
    Delete listings that are older than the specified number of weeks.
    """
    # Calculate the cutoff date (3 weeks ago)
    cutoff_date = (datetime.now() - timedelta(weeks=weeks)).isoformat()

    # Get listings older than the cutoff date
    response = (
        supabase.table("listings_v2")
        .select("id", "created_at")
        .is_("user_id", "null")
        .lt("created_at", cutoff_date)
        .execute()
    )

    old_listings = response.data
    print(f"Found {len(old_listings)} listings older than {weeks} weeks")

    # Track successfully deleted listings
    deleted_listings = []
    failed_listings = []

    for listing in old_listings:
        listing_id = listing["id"]
        created_at = listing["created_at"]

        print(f"Deleting old listing {listing_id} created at {created_at}")

        try:
            # Delete the listing from Supabase
            delete_response = (
                supabase.table("listings_v2").delete().eq("id", listing_id).execute()
            )
            deleted_listings.append(listing_id)
            print(f"Successfully deleted old listing {listing_id}")
        except Exception as e:
            print(f"Failed to delete old listing {listing_id}: {e}")
            failed_listings.append(listing_id)

    print(f"Deleted {len(deleted_listings)} old listings")
    if failed_listings:
        print(
            f"Failed to delete {len(failed_listings)} old listings: {failed_listings}"
        )

    return deleted_listings


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    print("=== Starting Cleanup Process ===")

    # Step 1: Delete listings where Facebook posts have been removed
    print("\n=== Checking for invalid Facebook listings ===")
    invalid_facebook_deleted = delete_invalid_facebook_listings()

    # Step 2: Delete listings older than 3 weeks
    print("\n=== Checking for old listings ===")
    old_listings_deleted = delete_old_listings(weeks=3)

    # Summary
    print("\n=== Cleanup Summary ===")
    print(f"Total invalid Facebook listings deleted: {len(invalid_facebook_deleted)}")
    print(f"Total old listings deleted: {len(old_listings_deleted)}")
    print("=== Cleanup Complete ===")
