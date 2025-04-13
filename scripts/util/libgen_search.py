'''
Focuses on just searching and finding matches of books then storing it in a CSV file

python3 libgen_search.py /home/stellajia/genai-copyright/data/all-books-copy.csv > libgen_search.txt
'''

import os
import requests
from bs4 import BeautifulSoup as BS
import wget
import csv 
import pandas as pd
import sys
import signal
import time
import string
from urllib.error import HTTPError
from requests.exceptions import ConnectTimeout
import random
from tqdm import tqdm

seperator = 126 * '━'

def find_longest_word(s):
    # Split the string into words
    words = s.split()
    
    # Initialize variables to keep track of the longest word and its length
    longest_word = ""
    longest_length = 0
    
    # Iterate over each word in the list
    for word in words:
        # Check if the current word is longer than the previous longest word
        if len(word) > longest_length:
            longest_word = word
            longest_length = len(word)
    
    return longest_word

def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

# Find best query
def find_best_query(book):
    book_words = book['title'].split(' ')
    if len(book['title']) > 36: # More than 36 characters
        book_words = book['title'].split(' ')
        if len(book_words) >= 4:
            query = ' '.join(book_words[:4]) # get first 4 words
        else:
            query = ' '.join(book_words[:2])
        return query
    else:
        return book['title'] 

def save_match(title, author, url):
    with open(f'saved_matches_{number}.txt', 'a') as f:
        f.write(f"{title},{author},{url}\n")

def load_last_processed():
    try:
        with open(last_processed_path, 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_last_processed(row):
    with open(last_processed_path, 'w') as f:
        f.write(str(row))


def search(query, max_retries=3):
    search_base = "http://libgen.rs/search.php?req={}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def"
    search_page = search_base.format(query.replace(' ', '+'))
    print("1. Link: ", search_page)
    
    retries = 0
    while retries < max_retries:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            page = requests.get(search_page, headers=headers, timeout=10)
            raw_html = page.text
            print("2. Get length of page text (test to see if actually getting something): ", len(raw_html))
            # print(raw_html)
            if len(raw_html) == 592:
                print(raw_html)
                return []
            
            soup = BS(raw_html, features='html5lib')
            results = []
            table_body = soup.find_all(valign="top")[1:]
            for row in table_body:
                item = {}
                data = row.findAll(width="500")
                for record in data:
                    href = record.find(name='a').get('href')
                    item['url'] = 'http://libgen.rs/' + href
                tds = row.find_all('td')
                tds = [td.text for td in tds]
                item['author'] = tds[1]
                item['title'] = tds[2]
                item['publisher'] = tds[3]
                try:
                    item['year'] = int(tds[4])
                except ValueError:
                    item['year'] = tds[4]
                item['pages'] = tds[5]
                item['langauge'] = tds[6]
                try:
                    if 'mb' in tds[7].lower():
                        item['size'] = float(tds[7].split()[0])
                    elif 'kb' in tds[7].lower():
                        item['size'] = float(tds[7].split()[0]) / 1000
                except ValueError:
                    item['size'] = tds[7]
                item['extension'] = tds[8]
                results.append(item)
            return results
        except ConnectTimeout:
            retries += 1
            print(f"Connection timed out. Retrying ({retries}/{max_retries})...")
            time.sleep(5)  # Add a delay before retrying

    print("Max retries exceeded. Returning None.")
    return None

def decide(results, target_book_title_query, author_name):
    '''
    results: list of books with the characteristics (author, title, etc) of each book stored
    [{'url': 'http://libgen.rs/book/index.php?md5=90674E59313A0CD2C66A6B36C591DC2E', 'author': 'Sigmund Freud', 'title': 'The Ego and the Id 0393001423', 'publisher': 'W. W. Norton & Company', 'year': 1989, 'pages': '63', 'langauge': 'English', 'size': 3.0, 'extension': 'pdf'}, {'url': 'http://libgen.rs/book/index.php?md5=76715DACB753E6736D772477593651F4', 'author': 'Sigmund Freud', 'title': 'The Ego and the Id [Paperback\xa0ed.] 0393001423, 9780393001426', 'publisher': 'W.W. Norton & Company (NY)', 'year': 1960, 'pages': '87', 'langauge': 'English', 'size': 0.135, 'extension': 'epub'}, {'url': 'http://libgen.rs/book/index.php?md5=8944056AB8C768B75779722BA69091AB', 'author': 'Sigmund Freud; Alan Tyson (editor); Alix Strachey (editor); Anna Freud; James Strachey', 'title': 'The standard edition of the complete psychological works of Sigmund Freud. Vol. 19, The ego and the id ; and other works : (1923-1925) 9780099426745, 0099426749', 'publisher': 'Hogart Press; The Institute of Psycho-Analysis; Vintage', 'year': 2001, 'pages': '[328]', 'langauge': 'English', 'size': 18.0, 'extension': 'pdf'}]
    
    target_book: row of the book where you can query out the title and author 
    '''
    print("1. Inside decide()")
    if results != []:
        
        # Find longest word in author name
        author_key = find_longest_word(author_name)
        author_key = remove_punctuation(author_key)
        print("Author key: ", author_key)
        print("2. Found longest author name")
        for result in results:
            if result['extension'] == 'epub':
                # Check if title matches because that must at least be similar
                print(f"Checking for match conditions between: {target_book_title_query} vs {result['title']} and {author_key} vs {result['author']}")
                if (target_book_title_query in result['title']) and (author_key in result['author']):
                    print("Found a epub file")
                    print(result)
                    # book_matches.append(result)
                    return result 
        for result in results:
            if result['extension'] == 'pdf': 
                print(f"Checking for match conditions between: {target_book_title_query} vs {result['title']} and {author_key} vs {result['author']}")
                if (target_book_title_query in result['title']) and (author_key in result['author']):
                    print("Found a pdf file")
                    return result
    else:
        return None
    
def do_it_all(book):
    try:
        print("FINDING...")
        print(f"Title: \"{book['title']}\"\nAuthor: \"{book['author']}\"")
        
        query_title = find_best_query(book)
        print("Libgen queries this: ", query_title)
        entries = search(query_title)
        print(entries)
        
        print("Output of entries (to  check what I can query out): ", entries)
        if entries != []:
            decision = decide(entries, query_title, book['author'])
            if decision != None:
                # SAVE MATCH
                save_match(book['title'], book['author'], decision['url'])
                print(f"\nSAVE MATCH ✅")
                print(f"Saved\"{book['title']}\" by \"{book['author']}.\"")
                print(seperator)
                return 1
            else:
                print("NOT FOUND ❌")
                print("Couldn't find a confident match.")
                print(seperator)
                return -1
    except (ValueError, TypeError, IndexError, FileNotFoundError, AttributeError, EOFError, KeyError) as e:
        print("INTERNAL ERROR 🛑")
        print(f"Error details: {e}")
        print("Something came up. Try this yourself.")
        print(seperator)
        return -1


file_path = sys.argv[1]
number = sys.argv[2]
df_path = file_path
books = pd.read_csv(df_path, low_memory=False)
# books['match'] = 0 # COMMET OUT LATER
print("Opened dataframe")
new_df_path = file_path
save_books_path = '/Users/stellajia/Desktop/Professional/data-innovation-lab/genai-copyright/get-libgen/output'
columns = ['title', 'author', 'url']
last_processed_path = f'last_processed_{number}.txt'

def save_df(df, new_filepath):
    df.to_csv(new_filepath, index=False)
    print("DataFrame saved successfully.")

def start():
    print("Book file: ", books.shape)
    total_rows = books.shape[0]
    
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        save_df(books, new_df_path)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    start_row = load_last_processed()
    for index, book in books.iloc[start_row:].iterrows():
        print(f"Getting Libgen for: {book['title']} ISBN: {book['isbn13']} (Row {index}/{total_rows})")
        if book['match'] == 1:
            print("SKIPPED THIS BOOK ⏭")
            print(
                f"\"{book['title']}\" by \"{book['author']}\" is checked Moving on...")
            print(seperator)
            continue 
        elif book['match'] == -1:
            print(f"\"{book['title']}\" by \"{book['author']}\" is trying again after error...")
            books.at[index, 'match'] = do_it_all(book)
            time.sleep(5)
            books.to_csv(new_df_path, index=False) 
        elif book['match'] == 0:
            books.at[index, 'match'] = do_it_all(book)
            time.sleep(5)
            books.to_csv(new_df_path, index=False)
        else:
            continue 
        save_last_processed(index)

start()