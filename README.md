# Logic

1. `main.py` is the scraper. it intercepts the graphql responses and extracts the data
1. `facebook_response_mapper.py` contains the extractors for the data. mainly using pydash and the nested paths to get the data
1. we are supposed to call `scraped_data_saver.py` to actually add to the dataframe and it also has logic for message hash and duplicate data cleanup
1. and once done we call `save_df` from `scraped_data_saver.py` which saves it to `scraped_data.csv` and hence it works
1. all of these is written into `scraped-data.csv`
1. `add_to_supabase.py` does the bulk of the work
    1. it reads the csv file and then for each row it uses data_extractor.py to call open ai and extract structured data
    1. it firs sets the supabase image uris and uploads the images and then extracts data
    1. and then inserts into supabase

So we basically need to run add_to_supabase.py once we are done scraping and writing to `scraped-data.csv`
