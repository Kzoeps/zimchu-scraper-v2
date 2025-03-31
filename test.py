# this is to test with open ai client to find those which are not listings

import os
import requests
import datetime
from dotenv import load_dotenv
from supabase_zimchu import supabase
from datetime import datetime, timedelta

load_dotenv()

response = supabase.table("listings_v2").select("id", "post_url").limit(1).execute()
# OPENAI_API_KEY: str = getenv("OPENAI_API_KEY")
# openAiClient = OpenAI(api_key=OPENAI_API_KEY, timeout=15)

for listing in response.data:
    post_url = listing["post_url"]

    if not post_url:
        continue
    response = requests.get(post_url)
    with open('response.txt', 'w') as file:
        if (response.status_code == 200):
            response_content = response.text.lower()
            file.write(response_content)
