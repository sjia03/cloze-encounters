
"""_summary_

Goal: Iterate over each book title and author => get book ID/link (create new dataframe holding book ID)

Basic attributes:
    1. Title (verify that it selected the right one)
    2. Author 
    3. Link
    4. First published date
    5. Genre
    6. Summary
    
Popularity metric attributes: 
    1. # of ratings
    2. # of reviews 
    3. Average stars 
    
Script layout:
    1. Search book based on "{file-name} {Author}"
    2. Find the correct link ***
    3. Save information (use https://github.com/maria-antoniak/goodreads-scraper/blob/master/get_books.py)

"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
 
def fetch_author_from_book_page(book_url):
    response = requests.get(book_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        author_name_element = soup.find('span', class_='ContributorLink__name')
        author_name = author_name_element.text if author_name_element else 'Name not found'
        print("Found author name: ", author_name)
        return author_name
    else:
        print("Failed to fetch the book page.")
        return None

def is_desired_book(link_text):
    undesired_keywords = ['summary', 'analysis', 'guide', 'review']
    return not any(keyword in link_text.lower() for keyword in undesired_keywords)

def get_goodreads_link(title, author, type=1):
    if type==1: # 
        query = f"{title}+{author}".replace(' ', '+')
    elif type==2: # Search w/o author
        query = f"{title}".replace(' ', '+')
    else:
        print("❌ Failed to fetch the search results.")
        return None  # Return None if the request fails
        
    url = f"https://www.goodreads.com/search?q={query}"
    print("🔍 Searching: ", url)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Analyze the top N search results for a better match
        results = soup.select('a.bookTitle')
        for result in results[:11]: # I don't want it to loop through all results...esp if the first one is already a summary
            # result_item = result.find_parent('tr')  # Assuming each result is contained within a table row
            
            link_text = result.text.strip()
            if is_desired_book(link_text):
                link = "https://www.goodreads.com" + result['href']
                author_name = fetch_author_from_book_page(link) # scraped from website
                author_parts = author.split() # saved name in file
                
                # Check if any part of the author's name is in the author info from the result
                print("Goodreads: ", author_name, "Target: ", author)
                if author_name == None:
                    continue 
                if any(part.lower() in author_name.lower() for part in author_parts):
                    print(f"✅ Found: {link}")
                    print(f"Author: {author_name}")
                    print("-" * 50)
                    return link
        
        # Fallback to title-only search if no suitable result is found
        type += 1
        print("🤞 Searching again w/o author: ", title, " Type: ", type)
        return get_goodreads_link(title, author, type)
    else:
        print("❌ Failed to fetch the search results.")
        return None  # Return None if the request fails

def get_goodreads_link_by_isbn(isbn):
    # Construct the query URL for ISBN search
    query = isbn.replace('-', '').replace(' ', '')  # Remove any dashes or spaces from ISBN
    url = f"https://www.goodreads.com/search?q={query}&search_type=books&search%5Bfield%5D=isbn"
    return url


def get_first_goodreads_link(title, author=''):
    # Initial attempt with both title and author
    link = get_goodreads_link(title, author)
    if link:
        return link
    else:
        # Fallback to title only if the first attempt fails
        return get_goodreads_link(title, author)


# print(fetch_author_from_book_page("https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye?from_search=true&from_srp=true&qid=Ha5cEsyfnS&rank=1"))

def add_book_link(row):
    # This function is designed to be safe for threading and doesn't modify global state.
    if pd.isnull(row['book_link']):
        print(f"Fetching: {row['Title']}")
        return get_goodreads_link_by_isbn(str(row['ISBN']))
    else:
        print(f"Already saved: {row['Title']}")
        return row['book_link']

def process_rows(df_slice):
    # Process a slice of the DataFrame, applying 'add_book_link' to each row.
    # Note: This returns a new DataFrame slice without modifying the original DataFrame.
    return df_slice.apply(lambda row: add_book_link(row), axis=1)

def main():
    csv_file_path = '/Users/stellajia/Desktop/Professional/data-innovation-lab/genai-copyright/books3-original-v2.csv'

    # Check if the CSV file exists to resume progress
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
    
    # Ensure the 'book_link' column exists
    if 'book_link' not in df.columns:
        df['book_link'] = None

    num_threads = 4  # Adjust based on your needs and system capabilities
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        # Split DataFrame into chunks and process each chunk in a separate thread
        chunks = np.array_split(df, num_threads)
        for chunk in chunks:
            futures.append(executor.submit(process_rows, chunk))

        # Collect results and combine them into a single DataFrame
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
        
        # Concatenate the results back into a single DataFrame
        updated_links = pd.concat(results)
        df['book_link'] = updated_links

    # Save the DataFrame to CSV after all threads have completed their execution
    df.to_csv(csv_file_path, index=False)
    print("Completed. The DataFrame has been saved to CSV.")

if __name__ == '__main__':
    main()