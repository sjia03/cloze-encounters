'''
Gets characteristics of a book from Goodreads given the Goodreads link

Characteristics include
1. year published
2. genre
3. number of ratings
4. number of reviews
5. average rating

Probably want to get more.
'''


import argparse
from datetime import datetime
import json
import os
import re
import time

from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed

def get_all_lists(soup):

    lists = []
    list_count_dict = {}

    if soup.find('a', text='More lists with this book...'):

        lists_url = soup.find('a', text='More lists with this book...')['href']

        source = urlopen('https://www.goodreads.com' + lists_url)
        soup = bs4.BeautifulSoup(source, 'lxml')
        lists += [' '.join(node.text.strip().split()) for node in soup.find_all('div', {'class': 'cell'})]

        i = 0
        while soup.find('a', {'class': 'next_page'}) and i <= 10:

            time.sleep(2)
            next_url = 'https://www.goodreads.com' + soup.find('a', {'class': 'next_page'})['href']
            source = urlopen(next_url)
            soup = bs4.BeautifulSoup(source, 'lxml')

            lists += [node.text for node in soup.find_all('div', {'class': 'cell'})]
            i += 1

        # Format lists text.
        for _list in lists:
            # _list_name = ' '.join(_list.split()[:-8])
            # _list_rank = int(_list.split()[-8][:-2]) 
            # _num_books_on_list = int(_list.split()[-5].replace(',', ''))
            # list_count_dict[_list_name] = _list_rank / float(_num_books_on_list)     # TODO: switch this back to raw counts
            _list_name = _list.split()[:-2][0]
            _list_count = int(_list.split()[-2].replace(',', ''))
            list_count_dict[_list_name] = _list_count

    return list_count_dict


def get_shelves(soup):

    shelf_count_dict = {}
    
    if soup.find('a', text='See top shelves…'):

        # Find shelves text.
        shelves_url = soup.find('a', text='See top shelves…')['href']
        source = urlopen('https://www.goodreads.com' + shelves_url)
        soup = bs4.BeautifulSoup(source, 'lxml')
        shelves = [' '.join(node.text.strip().split()) for node in soup.find_all('div', {'class': 'shelfStat'})]
        
        # Format shelves text.
        shelf_count_dict = {}
        for _shelf in shelves:
            _shelf_name = _shelf.split()[:-2][0]
            _shelf_count = int(_shelf.split()[-2].replace(',', ''))
            shelf_count_dict[_shelf_name] = _shelf_count

    return shelf_count_dict


def get_genres(soup):
    genres = []
    for genre_button in soup.find_all(class_="BookPageMetadataSection__genreButton"):
        # Extracting the text from the span with class 'Button__labelItem'
        genre_name = genre_button.find(class_="Button__labelItem").text
        genres.append(genre_name)
    print("Genres: ", genres)
    return genres


def get_series_name(soup):
    series = soup.find(id="bookSeries").find("a")
    if series:
        series_name = re.search(r'\((.*?)\)', series.text).group(1)
        return series_name
    else:
        return ""


def get_series_uri(soup):
    series = soup.find(id="bookSeries").find("a")
    if series:
        series_uri = series.get("href")
        return series_uri
    else:
        return ""

def get_top_5_other_editions(soup):
    other_editions = []
    for div in soup.findAll('div', {'class': 'otherEdition'}):
      other_editions.append(div.find('a')['href'])
    return other_editions

def get_isbn13(soup):
    # Find the div containing the ISBN number
    isbn_dt = soup.find('dt', string='ISBN')
    print("Find block: ", isbn_dt)
    
    if isbn_dt:
        isbn_dd = isbn_dt.find_next_sibling('dd')
        isbn_text = isbn_dd.get_text(strip=True)
        isbn_match_revised = re.search(r'(\d{13})', isbn_text)
        isbn_revised = isbn_match_revised.group(1) if isbn_match_revised else None

        if isbn_revised:
            print(f"Extracted ISBN: {isbn_revised}")
            return isbn_revised
    else:
        print("The specific HTML segment for ISBN13 was not found.")

    # if isbn_div:
    #     # Extract the ISBN number using a regular expression
    #     isbn_text = isbn_div.get_text(strip=True)
        
    #     if isbn_text:
    #         isbn = isbn_text.split()[0]
    #         print(f"Extracted ISBN: {isbn}")
    #         return isbn
    #     else:
    #         print("ISBN number not found in the specific segment.")
    # else:
    #     print("The specific HTML segment for ISBN13 was not found.")

def get_isbn(soup):
    # Find the div containing the ISBN number
    div_content = soup.find('span', {'class': 'Text Text__subdued'})
    print("ISBN10 attempt: ", div_content)

    if div_content:
        # Extract the ISBN-10 number using a regular expression
        isbn10_match = re.search(r'ISBN10:\s*([0-9Xx]{10})', str(div_content))
        if isbn10_match:
            isbn10_number = isbn10_match.group(1)  # This captures the matched ISBN-10 number
            print(f"Extracted ISBN-10: {isbn10_number}")
            return isbn10_number
        else:
            print("ISBN-10 number not found in the specific segment.")
    else:
        print("The specific HTML segment for ISBN10 was not found.")


def get_rating_distribution(soup):
    distribution = re.findall(r'renderRatingGraph\([\s]*\[[0-9,\s]+', str(soup))[0]
    distribution = ' '.join(distribution.split())
    distribution = [int(c.strip()) for c in distribution.split('[')[1].split(',')]
    distribution_dict = {'5 Stars': distribution[0],
                         '4 Stars': distribution[1],
                         '3 Stars': distribution[2],
                         '2 Stars': distribution[3],
                         '1 Star':  distribution[4]}
    return distribution_dict


def get_num_pages(soup):
    if soup.find('span', {'itemprop': 'numberOfPages'}):
        num_pages = soup.find('span', {'itemprop': 'numberOfPages'}).text.strip()
        return int(num_pages.split()[0])
    return ''


def get_year_first_published(soup):
    # Find the <p> element containing the publication date
    pub_info = soup.find('p', {'data-testid': 'publicationInfo'})

    if pub_info:
        # Extract the publication year using a regular expression
        year_match = re.search(r'\d{4}', pub_info.text)
        if year_match:
            publication_year = year_match.group(0)  # This captures the matched year
            print(f"Extracted publication year: {publication_year}")
            return publication_year
        else:
            print("Publication year not found in the text.")
            return -1
    else:
        print("Publication information not found.")
        return -1

def get_id(bookid):
    pattern = re.compile("([^.-]+)")
    return pattern.search(bookid).group()

def get_cover_image_uri(soup):
    series = soup.find('img', id='coverImage')
    if series:
        series_uri = series.get('src')
        return series_uri
    else:
        return ""
    
def get_num_ratings(soup):
    # Find the span containing the ratings count
    ratings_span = soup.find('span', {'data-testid': 'ratingsCount'})

    if ratings_span:
        # Extract the number of ratings using a regular expression
        ratings_text = ratings_span.text  # Get the text of the ratings span
        ratings_number = re.search(r'(\d{1,3}(?:,\d{3})*)', ratings_text).group(1)  # Match the number with commas
        ratings = int(ratings_number.replace(',', ''))  # Convert to an integer after removing commas
        print("Number of ratings: ", ratings)
        return ratings
    else:
        print("Number of ratings: ", -1)
        return -1
    
def get_num_reviews(soup):
    # Find the span containing the reviews count
    reviews_span = soup.find('span', {'data-testid': 'reviewsCount'})

    # Extract the number of reviews using a regular expression
    if reviews_span:
        reviews_text = reviews_span.text  # Get the text of the reviews span
        reviews_number = re.search(r'(\d{1,3}(?:,\d{3})*)', reviews_text).group(1)  # Match the number with commas
        reviews = int(reviews_number.replace(',', ''))  # Convert to an integer after removing commas
        print("Number of reviews: ", reviews)
        if reviews == 'None':
            return -1
        return reviews
    else:
        print("Number of reviews: ", -1)
        return -1

def extract_number_from_html(html):
    html = str(html)
    if isinstance(html, str):
        match = re.search(r'>\s*([0-9.]+)\s*<', html)
        if match:
            return float(match.group(1))
        else:
            return html
    else:
        return html

def get_avg_ratings(soup):
    avg_rating = soup.find('div', class_='RatingStatistics__rating')
    avg_rating =  extract_number_from_html(avg_rating)
    if avg_rating == 'None':
        print("Average rating: ",-1)
        return -1
    print("Average rating: ",avg_rating)
    return avg_rating

    
def scrape_book(url):
    # url = 'https://www.goodreads.com/book/show/' + book_id
    source = urlopen(url)
    soup = bs4.BeautifulSoup(source, 'html.parser')

    time.sleep(2)

    return {
            # 'isbn':                 get_isbn(soup),
            # 'isbn13':               get_isbn13(soup),
            'year_first_published': get_year_first_published(soup),
            # 'num_pages':            get_num_pages(soup), # FIX THIS!!!
            'genres':               get_genres(soup), # FIX THIS!!!
            'num_ratings':          get_num_ratings(soup),
            'num_reviews':          get_num_reviews(soup),
            'average_rating':       get_avg_ratings(soup)
            # 'rating_distribution':  get_rating_distribution(soup)
            }

def condense_books(books_directory_path):

    books = []
    
    # Look for all the files in the directory and if they contain "book-metadata," then load them all and condense them into a single file
    for file_name in os.listdir(books_directory_path):
        if file_name.endswith('.json') and not file_name.startswith('.') and file_name != "all_books.json" and "book-metadata" in file_name:
            _book = json.load(open(books_directory_path + '/' + file_name, 'r')) #, encoding='utf-8', errors='ignore'))
            books.append(_book)

    return books

# Assuming all necessary imports are done, including bs4, urlopen, etc.

# def main(file_path):
#     df = pd.read_csv(file_path)
#     # List of new columns to be added
#     new_columns = ['year_first_published', 
#                    'genres', 'num_ratings', 'num_reviews', 
#                    'average_rating']
    
#     # Check if new columns exist, if not, add them with default values
#     for col in new_columns:
#         if col not in df.columns:
#             df[col] = None  # or pd.NA for pandas >= 1.0.0
    
#     # Iterate through DataFrame
#     for index, row in df.iterrows():
#         # Check if the row already contains data in one of the new columns
#         if pd.isnull(row['num_ratings']) and not pd.isnull(row['book_link']):  
#             print("----\n📚 Processing book at index {}: {}".format(index, row['book_link']))
            
#             # Call the scrape_book function
#             scraped_data = scrape_book(row['book_link'])
            
#             # Update row with scraped data
#             for col in new_columns:
#                 df.at[index, col] = scraped_data[col]
            
#             print("✅ Successfully updated book: {}".format(row['Title']))
            
#             # Save the DataFrame to file after updating each row
#             df.to_csv(file_path, index=False)
#             print("💾 Data saved to file.")
#         elif pd.isnull(row['book_link']):
#             print("----\n🔍 Book at index {} does not have a link: {}".format(index, row['Title']))
#         else:
#             print("----\n🔍 Book at index {} already updated: {}".format(index, row['Title']))
    
#     return df

def scrape_and_update_row(index, row, df, new_columns, file_path):
    if pd.isnull(row['num_ratings']) and not pd.isnull(row['book_link']):  
        print(f"----\n📚 Processing book at index {index}: {row['book_link']}")
        
        # Call the scrape_book function
        scraped_data = scrape_book(row['book_link'])
        
        # Update row with scraped data
        for col in new_columns:
            df.at[index, col] = scraped_data[col] # Check
        
        print(f"✅ Successfully updated book: {row['Title']}")
        # Save the DataFrame to file after updating each row
        # df.to_csv(file_path, index=False) # Check: pass by address instead value
        
        # Could try creating a txt file and add info to it (impact of write mode on concurrent access)
        
        print("💾 Data saved to file.")
    elif pd.isnull(row['book_link']):
        print(f"----\n🔍 Book at index {index} does not have a link: {row['Title']}")
    else:
        print(f"----\n🔍 Book at index {index} already updated: {row['Title']}")

def main(file_path):
    df = pd.read_csv(file_path) 
    new_columns = ['year_first_published', 'genres', 'num_ratings', 'num_reviews', 'average_rating']
    
    for col in new_columns:
        if col not in df.columns:
            df[col] = None
    
    # Use ThreadPoolExecutor to process rows in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_and_update_row, index, row, df, new_columns, file_path) 
                   for index, row in df.iterrows()]
        
        # Optional: use as_completed to handle futures as they are completed
        for future in as_completed(futures):
            future.result()  # This line is optional, it ensures any exceptions are raised
    
    df.to_csv(file_path, index=False)
    return df


# Assuming you have a DataFrame named 'books_df' and a file path 'books_file.csv'
# file_path = 'books_file.csv'
# books_df = pd.read_csv(file_path)
# updated_books_df = main(books_df, file_path)




if __name__ == '__main__':
    file_path = '/Users/stellajia/Desktop/Professional/data-innovation-lab/genai-copyright/books3-original.csv'
    df = main(file_path)
    df.to_csv('/Users/stellajia/Desktop/Professional/data-innovation-lab/genai-copyright/books3-original.csv')