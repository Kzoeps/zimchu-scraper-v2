from os import getenv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL: str = getenv("SUPABASE_URL")
ADMIN_KEY: str = getenv("SUPABASE_ADMIN_KEY")

supabase: Client = create_client(SUPABASE_URL, ADMIN_KEY)
