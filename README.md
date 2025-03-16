# Logic

1. `main.py` is the scraper. it intercepts the graphql responses and extracts the data
2. `facebook_response_mapper.py` contains the extractors for the data. mainly using pydash and the nested paths to get the data
3. all of these is written into `scraped-data.csv`
4. `add_to_supabase.py` does the bulk of the work
    1. it reads the csv file and then for each row it uses data_extractor.py to call open ai and extract structured data
    2. it firs sets the supabase image uris and uploads the images and then extracts data
    3. and then inserts into supabase



So we basically need to run add_to_supabase.py once we are done scraping and writing to `scraped-data.csv`