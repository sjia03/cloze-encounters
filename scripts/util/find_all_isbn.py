'''
Find all ISBN's of a book so can verify that all versions of a book don't exist in Books3 
This script specifically is to be run on Books3 data (get all ISBN's for every book in Books3)
'''

import requests
import pandas as pd
import time
import signal
import sys

def match_any_author_words(author_from_df, api_authors_list):
    author_words = set(str(author_from_df).replace(';', ' ').replace(',', ' ').split())
    for api_author in api_authors_list:
        api_author_words = set(api_author.split(', '))
        if author_words & api_author_words:
            return True
    return False

# EDIT: MIGHT NEED TO EDIT THIS TO MAKE SURE IT ACTUALLY FINDS THE RIGHT BOOKS
def search_books_by_title_and_author(api_key, title, author):
    url = "https://api2.isbndb.com/books/{query}"
    headers = {
        "Authorization": api_key
    }
   
    query = f"{title}"  # Adjust if the API expects a different format.
    response = requests.get(url.format(query=query), headers=headers)
    if response.status_code == 200:
        books = response.json()['books']
                
        isbns = []
        isbn13s = []
            
        for book in books:
            if 'authors' in book and match_any_author_words(author, book['authors']):
                print("Found match between: ", author, "AND", book['authors'])
                isbns.append(book['isbn'])
                isbn13s.append(book['isbn13'])
            else:
                continue  # Skip to the next book if 'authors' key is not present or the match function fails
        return isbns, isbn13s
    
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        return [-99], [-99]
    
def update_isbn(df, api_key):
    total_rows = len(df)
    # Loop through the dataframe from the last row to the first row
    for index in range(total_rows - 1, -1, -1):
        row = df.iloc[index]
        if pd.isna(row['author']):
            print("👀 Author not recorded")
            df.at[index, 'isbn10_v2'] = []  # Update the ISBN column
            df.at[index, 'isbn13_v2'] = []
            continue

        if (pd.isna(row['isbn10_v2']) and pd.isna(row['isbn13_v2'])) or (row['isbn10_v2'] == [] and row['isbn13_v2'] == []):
            print(f"Checking: {row['title']} (Row {index + 1}/{total_rows})")
            time.sleep(1)
            isbn10s, isbn13s = search_books_by_title_and_author(api_key, row['title'], row['author'])
            if (isbn10s != [-99]) or (isbn13s != [-99]):
                print("✅ Found ISBN values for at least one of them")
                df.at[index, 'isbn10_v2'] = isbn10s  # Update the ISBN column
                df.at[index, 'isbn13_v2'] = isbn13s
            else:
                print("❌ Could not find ISBN")
                df.at[index, 'isbn10_v2'] = []  # Update the ISBN column
                df.at[index, 'isbn13_v2'] = []
            print("-"*10)
        else:
            print("Already checked: ", row['title'])

def save_df(df, new_filepath):
    df.to_csv(new_filepath, index=False)
    print("DataFrame saved successfully.")

def main():
    api_key = ""
    file_path = '/Users/stellajia/Desktop/Professional/data-innovation-lab/genai-copyright/books3-final/books3_scraped_all.csv'
    new_filepath = '/Users/stellajia/Desktop/Professional/data-innovation-lab/genai-copyright/books3-final/books3_scraped_all.csv'
    df = pd.read_csv(file_path)
    
    print('Data size: ', df.shape)
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        save_df(df, new_filepath)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        update_isbn(df, api_key)
    except Exception as e:
        print(f"Error occurred during update_isbns: {str(e)}")
    finally:
        # Save final DataFrame
        save_df(df, new_filepath)

            
if __name__ == '__main__':
    main()
    
        
        
        


