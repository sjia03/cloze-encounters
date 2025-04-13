'''
python3 libgen_download.py saved_matches_pt2.csv > saved_matches_pt2_output.txt
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
import execjs
from tqdm import tqdm

def download(url, save_name, save_books_path, max_retries=3, retry_delay=5):
    save_path = os.path.join(save_books_path, save_name)
    
    # Attempt to download the file
    for i in range(max_retries):
        try:
            response = requests.get(url, stream=True)
            
            # TODO: print response variable to better understand INTERNAL ERROR issue
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte
                t = tqdm(total=total_size, unit='iB', unit_scale=True)
                
                with open(save_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        t.update(len(data))
                        file.write(data)
                
                t.close()
                
                if total_size != 0 and t.n != total_size:
                    print("ERROR, something went wrong")
                else:
                    print(f"File downloaded: {save_path}")
                    return True
            else:
                print(f"Failed to download file: {url}. Retrying...")
        except Exception as e:
            print(f"Exception occurred: {e}. Retrying...")
        
        time.sleep(retry_delay)
    
    # All retries failed
    print(f"Failed to download file after {max_retries} retries: {url}")
    return False

seperator = "*" * 10

'''
def mirrors(url):
    page = requests.get(url)
    print("1. Retrieved html info from url: ", url)
    raw_html = page.text
    soup = BS(raw_html, features='html5lib')
    mirrors_messed = soup.find_all(valign="top")[-4]
    mirrors_better = mirrors_messed.find_all(name='a')
    mirrors = []
    for mirror in mirrors_better[:4]:
        item = {}
        item['name'] = mirror.get('title')
        item['url'] = mirror.get('href')
        # item['extension'] = item['url'].split('.')[1]
        mirrors.append(item)
    print("2. Got mirrors")
    return mirrors
'''
def mirrors(url):
    page = requests.get(url)
    print("1. Retrieved html info from url: ", url)
    raw_html = page.text
    soup = BS(raw_html, features='html5lib')
    mirrors_list = soup.find_all(valign="top")

    if len(mirrors_list) < 4:
        print(f"ERROR: Expected at least 4 elements, but got {len(mirrors_list)}")
        print(f"mirrors_list: {mirrors_list}")
        return []

    mirrors_messed = mirrors_list[-4]
    mirrors_better = mirrors_messed.find_all(name='a')
    mirrors = []
    for mirror in mirrors_better[:4]:
        item = {}
        item['name'] = mirror.get('title')
        item['url'] = mirror.get('href')
        mirrors.append(item)
    print("2. Got mirrors")
    return mirrors

'''
def mirror_to_url(mirrs, mirror):
    print("3. Inside mirror_to_url function")
    if mirror == 'gen-lib-rus-ec':
        redirect = mirrs[0]['url']
        print("Redirect: ", redirect)
        page = requests.get(redirect)
        raw_html = page.text
        soup = BS(raw_html, features='html5lib')
        url = soup.h2.find(name='a').get('href')
        print("Returned proper URL")
        return url
    if mirror == 'libgen-lc':
        redirect = mirrs[1]['url']
        print("Redirect: ", redirect)
        page = requests.get(redirect)
        raw_html = page.text
        soup = BS(raw_html, features='html5lib')
        url = soup.body.table.tbody.tr.find_all(
            'td')[1].find(name='a').get('href')
        print("Returned proper URL")
        return url
    else:
        pass
'''

def mirror_to_url(mirrs, mirror):
    print("3. Inside mirror_to_url function")
    if not mirrs:
        print("ERROR: mirrors list is empty")
        return None

    try:
        if mirror == 'gen-lib-rus-ec':
            if len(mirrs) < 1:
                print(f"ERROR: Expected at least 1 mirror, but got {len(mirrs)}")
                return None

            redirect = mirrs[0]['url']
            print("Redirect: ", redirect)
            page = requests.get(redirect)
            raw_html = page.text
            soup = BS(raw_html, features='html5lib')
            url = soup.h2.find(name='a').get('href')
            print("Returned proper URL")
            return url

        if mirror == 'libgen-lc':
            if len(mirrs) < 2:
                print(f"ERROR: Expected at least 2 mirrors, but got {len(mirrs)}")
                return None

            redirect = mirrs[1]['url']
            print("Redirect: ", redirect)
            page = requests.get(redirect)
            raw_html = page.text
            soup = BS(raw_html, features='html5lib')
            url = soup.body.table.tbody.tr.find_all('td')[1].find(name='a').get('href')
            print("Returned proper URL")
            return url

    except Exception as e:
        print(f"ERROR: Exception occurred while processing mirrors: {e}")
        return None

    print("ERROR: Unsupported mirror")
    return None

'''
def do_it_all(book, mirror, save_books_path):

    
    try:
        print("DOWNLOADING...")
        print(f"{book['Title_Author']}")
        
        if book['Link'] != None:
            
            # DOWNLOAD book 
            url = book['Link']
            mirrs = mirrors(url)
            download_url = mirror_to_url(mirrs, mirror)
            extension = download_url.split('.')[-1]
                
            print("URL:", download_url, sep='\n')
            save_name = book['Title_Author'].lower().replace(" ", "-") + '.' + extension
            download_status = download(download_url, save_name, save_books_path)
            # book['downloaded'] = True
            if download_status == True:
                print(f"\nDOWNLOADED ✅")
                print(f"Downloaded\"{book['Title_Author']}\"")
                print(seperator)

                return 1
            else:
                # print("URL:", download_url, sep='\n')
                print("INTERNAL ERROR 🛑")
                print(f"Error details: {download_status}")
                print("Something came up. Try this yourself.")
                print(seperator)
                return -1
        else:
            # print("URL:", download_url, sep='\n')
            print("NOT FOUND ❌")
            print("Couldn't find a confident file. Try this yourself.")
            print(seperator)
            return -1
        
    except (ValueError, TypeError, IndexError, FileNotFoundError, AttributeError, EOFError, KeyError) as e:
        url = book['Link']
        mirrs = mirrors(url)
        download_url = mirror_to_url(mirrs, mirror)
        extension = download_url.split('.')[-1]
        
        print("URL:", download_url, sep='\n')
        print("INTERNAL ERROR 🛑")
        print(f"Error details: {e}")
        print("Something came up. Try this yourself.")
        print(seperator)
        return -1
'''
def do_it_all(book, mirror, save_books_path):
    try:
        print("DOWNLOADING...")
        print(f"{book['Title_Author']}")
        
        if book['Link'] != None:
            # DOWNLOAD book 
            url = book['Link']
            mirrs = mirrors(url)
            download_url = mirror_to_url(mirrs, mirror)

            if download_url is None:
                print("Failed to retrieve download URL.")
                return -1

            extension = download_url.split('.')[-1]
            
            print("URL:", download_url, sep='\n')
            save_name = book['Title_Author'].lower().replace(" ", "-") + '.' + extension
            download_status = download(download_url, save_name, save_books_path)
            if download_status:
                print(f"\nDOWNLOADED ✅")
                print(f"Downloaded \"{book['Title_Author']}\"")
                print(seperator)
                return 1
            else:
                print("INTERNAL ERROR 🛑")
                print(f"Error details: {download_status}")
                print("Something came up. Try this yourself.")
                print(seperator)
                return -1
        else:
            print("NOT FOUND ❌")
            print("Couldn't find a confident file. Try this yourself.")
            print(seperator)
            return -1
        
    except (ValueError, TypeError, IndexError, FileNotFoundError, AttributeError, EOFError, KeyError) as e:
        print("INTERNAL ERROR 🛑")
        print(f"Error details: {e}")
        print("Something came up. Try this yourself.")
        print(seperator)
        return -1

        
# EDIT: in the path to call this script, it will call the path to the csv 
csv_file_path = sys.argv[1]

# Read the CSV file into a DataFrame
books = pd.read_csv(csv_file_path)

# EDIT: folder where books will be downloaded (ensure it already exists)
save_books_path = '/Users/srushtipawar/Documents/NYU Courant/Spring 24/UCB/combined_libgen_search/final_combined/libgen-files'

def start():
    print("Book file: ", books.shape)
    total_rows = books.shape[0]
    
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        save_df(books, csv_file_path)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    for index, book in books.iterrows():
        print(f"Getting Libgen for: {book['Title_Author']} (Row {index}/{total_rows})")
        if book['downloaded'] == 1: # true
            print("SKIPPED THIS BOOK ⏭")
            print(
                f"\"{book['Title_Author']}\" is downloaded Moving on...")
            print(seperator)
            # update_csv(csv_file_path, book['title'], book['year'], book['author'], book['isbn'], book['copyright'], book['books3'])
        elif book['downloaded'] == -1: # can not find
            print("TRYING THIS BOOK again for this round")
            # print("This book HAD an error")
            # Retry running the failed to download books
            books.at[index, 'downloaded'] = do_it_all(book, mirror, save_books_path)
            time.sleep(5)
            books.to_csv(csv_file_path, index = False)
            print(seperator)
        elif book['downloaded'] == 0: # false (have not tried downloading yet)
            # print("This book could not be found")
            books.at[index, 'downloaded'] = do_it_all(book, mirror, save_books_path)
            time.sleep(5)
            books.to_csv(csv_file_path, index=False)
        else:
            print("SKIPPED THIS BOOK ⏭")
            print(
                f"\"{book['Title_Author']}\" was not found. Moving on...")
            print(seperator)



def save_df(df, new_filepath):
    df.to_csv(new_filepath, index=False)
    print("DataFrame saved successfully.")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    save_df(books, csv_file_path)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

mirror = 'gen-lib-rus-ec'

start()

# Save the updated DataFrame back to the CSV file or to a new file
# df.to_csv('updated_' + csv_file_path, index=False)
