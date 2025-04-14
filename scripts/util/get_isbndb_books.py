import requests
import pandas as pd
import time
from tqdm import tqdm

# Your keywords and years range
stop_words = ['the', 'a', 'an', 'and', 'of', 'in', 'to', 'with']
non_stop_words =['journey', 'secret', 'night', 'love', 'war', 'magic',
            'dream', 'city', 'adventure', 'mystery', 'life', 'world', 'death', 'quest', 'hero', 'shadow', 'light',
            'time', 'heart', 'star'] 
years_range = range(1970, 1990)  # Max 2023 b/c no books in books3 should be above 2022
page_size = 1000
stop_word_page_number = 1
non_stop_word_page_number = 1

# Your REST API key
# headers = 

# Base URL
base_url = "https://api2.isbndb.com/books/"

# CSV file path
csv_file_path = "isbn_books_metadata.csv"

# Initialize the CSV file with headers
pd.DataFrame(columns=['Title', 'ISBN-13', 'ISBN-10', 'Year', 'Subjects','Authors']).to_csv(csv_file_path, index=False)

# Counter to keep track of requests for rate limiting
request_counter = 0

for category in [('stop', stop_words, stop_word_page_number), ('non-stop', non_stop_words, non_stop_word_page_number)]:
    word_type, words, page_number = category
    for word in tqdm(words, desc=f"Processing {word_type} words"):
        for year in tqdm(years_range, desc=f"Years for word '{word}'"):
            print(f"Fetching books for {word_type} word '{word}' in year {year}")
            # Construct the request URL
            url = f"{base_url}{word}?page={page_number}&pageSize={page_size}&year={year}"

            # Make the request
            response = requests.get(url, headers=headers)
            request_counter += 1

            # Optional: Check the status code before processing the response
            if response.status_code == 200:
                data = response.json()

                books_list = [{
                    "Title": book["title"],
                    "ISBN-13": book.get("isbn13", ""),
                    "ISBN-10": book.get("isbn10", ""),
                    "Year": book["date_published"][:4] if "date_published" in book else "",
                    "Subjects": ", ".join(book.get("subjects", [])),
                    "Authors": ", ".join(book.get("authors", []))
                } for book in data["books"]]

                # Convert the list to DataFrame (saves after each year)
                books_df = pd.DataFrame(books_list)

                # Append to the CSV file without headers (since it's already initialized)
                books_df.to_csv(csv_file_path, mode='a', header=False, index=False)
            else:
                print(f"Error fetching data for {word_type} word '{word}' in year {year}: {response.status_code}")

            # Be mindful of the service's rate limits; add a delay if needed
            if request_counter % 3 == 0:
                time.sleep(1)
