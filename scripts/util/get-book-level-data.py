#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import ast

os.chdir("/Users/stellajia/Dropbox/23.Copyright-LLMs")

query_df = pd.read_csv('filedata/query-level-final.csv')
print(query_df.columns)
print(query_df.shape)

query_df.head()

# Add Fiction/Nonfiction Column ----------------------------------------------------------------
# Function to safely parse the 'genres' column
def safe_literal_eval(genre_str):
    try:
        return ast.literal_eval(genre_str) if isinstance(genre_str, str) else genre_str
    except (ValueError, SyntaxError):
        return []  # Return an empty list for malformed entries

# Apply the function to convert genres
query_df['genres'] = query_df['genres'].apply(safe_literal_eval)

# Fiction and Nonfiction genre sets based on your classification
fiction_genres = [ 
    'Gay Fiction', 'Harlequin', 'Dystopia', 'Supernatural', 'Regency Romance', 'Harlequin Romance',
    'Military Fiction', 'Romantic Suspense', 'Contemporary Romance', 'Science Fiction Fantasy',
    'New Adult', 'Military Fiction', 'Historical Romance', 'Erotica', 'Romance', 'Science Fiction',
    'Classic Literature', 'Historical', 'Erotic Romance', 'Fantasy', 'Realistic Fiction', 'Teen',
    'Retellings', 'Mystery', 'Romantic Suspense', 'Chick Lit', 'Urban Fantasy', 'Epic Fantasy',
    'Medieval Romance', 'Urban', 'Teen', 'Futuristic', 'Western', 'High Fantasy', 'Wildlife', 'Novella',
    'Urban Fantasy', 'Paranormal', 'Humor', 'Pop Culture', 'Chick Lit', 'Urban Fantasy', 'Historical Fiction',
    'Fantasy', 'Historical Romance', 'Steampunk', 'Science Fiction', 'Romance', 'Science Fiction Fantasy',
    'Adventure', 'Suspense', 'Thriller', 'Mystery Thriller', 'Novel', 'Family Saga', 'Fantasy', 'Classics', 'Literature', 'African American',
    'Mythology', 'Civil War Eastern Theater', 'Video Games', 'German Literature', 'Asian Literature', 'Spanish Literature', 'Japanese Literature',
    'Russian Literature', 'Irish Literature', 'Indonesian Literature', 'British Literature', 'Spanish Literature', 'Russian Literature',
    'Japanese Literature', 'Christmas', 'Horror', 'Short Stories', 'Theatre'
]

nonfiction_genres = [ 
    'Theory', 'Sewing', 'Nature', 'Anthropology', 'Fashion', 'Church History', 'Spanish History',
    'Engineering', 'Nutrition', 'Old Testament', 'Military History', 'Cookbooks', 'Political Science',
    'School', 'Books About Books', 'Literary Criticism', 'Psychoanalysis', 'Accounting', 'Management',
    'Money', 'Science', 'Geography', 'History', 'Social Media', 'Biography', 'Health',
    'Mental Health', 'Research', 'Dogs', 'Labor', 'Geology', 'Drama', 'History Of Science', 'Food History',
    'Baseball', 'Class', 'Language', 'Grad School', 'Communication', 'Biology',
    'Australia', 'Social Change', 'True Crime', 'The United States Of America', 'Aviation', 'Zen', 'Russia',
    'Personal Development', 'World History', 'Society', 'Judaism', 'Spiritualism', 'American Civil War',
    'European History', 'Ireland', 'Physics', 'Mathematics', 'Classical Studies', 'Evangelism',
    'Japan', 'Memoir', 'Art History', 'Archaeology', 'Psychiatry', 'Electrical Engineering', 'Reference',
    'Guides', 'Audiobook', 'Computers', 'Programming', 'Self Help', 'Music', 'Victorian', 'Design',
    'Ecology', 'Textbooks', 'Economics', 'Politics', 'Judaica', 'Sociology', 'Plays',
    'Childrens', 'Football', 'Islam', 'Death', 'Sexuality', 'Role Playing Games', 'Leadership', 'Food and Wine',
    'Genetics', 'Contemporary', 'Business', 'Medieval History', 'Road Trip', 'Racing', 'Angels', 'Health Care',
    'Roman', 'Logic', 'Witchcraft', 'Folklore', '20th Century', 'Anglo Saxon', 'New Testament', 'Food', 'Queer',
    'Eugenics', 'Medicine', 'Neuroscience', 'Ancient', 'Urban Planning', 'Travel',
    'Social Science', 'Faith', 'Ghosts', 'Traditional Chinese Medicine', 'Marriage', 'Cultural', 'Theology',
    'Jazz', 'Gothic', 'Photography', 'Cults', 'Journalism', 'Russian History', 'Christianity', 'War', 'Culinary',
    'Demons', 'Theosophy', 'International Relations', 'India', 'Russian Revolution', 'Technical', 'Fairies',
    'Christian Living', 'World War II', 'Soviet Union', 'Taoism', 'Artificial Intelligence', 
    'Ethnography', 'Sports', 'Parenting', 'Brazil', 'Medical',
    'Naval History', 'Vegan', 'Horror', 'Buddhism', 'Astronomy', 'Short Stories', 'Vampires', 'Spain', 'Law',
    'Entrepreneurship', 'World War I', 'Palaeontology', 'Wine', 'Hinduism', 'Health', 'Civil War', 'Civil War History',
    'Greece', 'Menage', 'Anthologies', 'LGBT', 'French Revolution', 'Productivity', 'Mysticism', 'Astrology',
    'College', 'Website Design', 'Feminism', 'Regency', 'Environment', 'Linguistics', 'Philosophy', 'American',
    'Historical Fiction', 'Technology', 'Church',
    'Teaching', 'Poetry', 'Finance', 'Latin American History', 'China', 'Psychology', 'Natural History', 'Adult Fiction',
    'Academic', 'Fitness', 'Cycling', 'Film', 'Gaming', 'Chess', 'Female Authors', 'Holocaust', '18th Century',
    'Computer Science', 'Animals', 'Israel', 'Horticulture', 'Martial Arts', 'Overland Campaign', 'Crime',
    'Shapeshifters', 'Algebra', 'Metaphysics', 'Criticism', 'Photography', 'Cults', 'Adult', 'Us Presidents',
    'Magick', 'Journalism', 'Russian History', 'Christianity', 'War', 'Culinary', 'Art', 'Demons', 'Theosophy',
    'International Relations', 'India', 'Russian Revolution', 'Technical', 'Fairies', 'Christian Living', 'World War II',
    'Soviet Union', 'Taoism', 'Artificial Intelligence', 'Ethnography', 'Sports', 'Parenting',
     'Gay', 'Medical', 'Naval History', 'Vegan',
    'Buddhism', 'Astronomy', 'Vampires', 'Spain', 'Law', 'Entrepreneurship', 'World War I',
    'Palaeontology', 'Wine', 'Hinduism', 'Health', 'Civil War', 'Paranormal Romance', 'Greece', 'Menage', 'Anthologies',
    'Jewish', 'Fantasy', 'Software', 'Cities', 'Disability Studies', 'Harlequin Desire', 'Ancient History', 'Tarot',
    'LGBT', 'French Revolution', 'Productivity', 'Lds', 'Mystery', 'Prayer', 'Drawing', 'Science', 'Hackers', 'Unfinished', 'Architecture', 'Writing', 'Autistic Spectrum Disorder', 'Nursing',
    'Education', 'Africa', 'Social Work', 'Religion', 'Christian', 'Cooking', 'Sex Work', 'Counselling', 'Cars', 'Physical Therapy', 'Spirituality', 'Race', 'Westerns', 'Essays', 'Occult'
]


def classify_genre(genres):
    if genres is None or len(genres) == 0:
        return np.nan, np.nan  # skip if genres is empty or null
    
    # Step 1: Check for 'Fiction' or 'Nonfiction' in genres
    if "fiction" in genres:
        return 1, 0
    elif "nonfiction" in genres:
        return 0, 1

    # Step 2: Check against fictions_list and nonfictions_list if needed
    if any(genre in fiction_genres for genre in genres):
        return 1, 0
    elif any(genre in nonfiction_genres for genre in genres):
        return 0, 1
    
    return np.nan, np.nan  # neither fiction nor nonfiction identified

# Apply the function to create the Fiction and Nonfiction columns
query_df[['fiction', 'nonfiction']] = query_df['genres'].apply(lambda x: pd.Series(classify_genre(x)))



# In[31]:


query_df['genres'] = query_df['genres'].apply(lambda x: np.nan if isinstance(x, list) and len(x) == 0 else x)
query_df['fiction'] = query_df['fiction'].astype('Int64')
query_df['nonfiction'] = query_df['nonfiction'].astype('Int64')

# Group Data by Book ----------------------------------------------------------------

# for each model answer column (gpt35, gpt4o, claude, llama8b, llama70b, gemini) create a new column with the score which is 0 or 1 based on if it matches correct_answer

model_columns = ['gpt35', 'gpt4o', 'claude', 'llama8b', 'llama70b', 'gemini']
correct_answer_column = 'correct_answer'

for model in model_columns:
    query_df[f'{model}_score'] = (query_df[f'{model}_answer'] == query_df[correct_answer_column]).astype(int)

agg_dict = {f'{model}_score': 'mean' for model in model_columns}
agg_dict.update({col: 'first' for col in query_df.columns if col not in agg_dict})

book_level_df = (
    query_df.groupby('book_id', as_index=False)  # Prevents map_file_name from becoming an index
    .agg(agg_dict)
    .assign(count=query_df.groupby('book_id').size().values)
)

# Remove _answer columns safely
book_level_df = book_level_df.drop(
    columns=[f'{model}_answer' for model in model_columns if f'{model}_answer' in book_level_df.columns]
)

book_level_df = book_level_df.reset_index()
book_level_df.head(2)


# Add popularity buckets ----------------------------------------------------------------

# Create popularity bins
bins = [0, 10, 100, 1000, 7000000]
labels = ['0-10', '10-100', '100-1000', '1000+']
book_level_df['popularity'] = pd.cut(book_level_df['num_ratings'], bins=bins, labels=labels, include_lowest=True)



# Add Shares ----------------------------------------------------------------
shares = pd.read_csv('filedata/shares.csv')

merged_data = pd.merge(book_level_df, shares, on='pub_year', how='left', indicator=True) # For non-overlapping years should I put 0???
merged_data = merged_data[merged_data['_merge'] == 'both']
merged_data.drop(columns=['_merge'], inplace=True)
# rename Shares to shares
merged_data.rename(columns={'Shares': 'shares'}, inplace=True)
print("final data shape: ", merged_data.shape)

# this version of the data has all other years set to 0
merged_data.to_csv('tmp/book-level-stella.csv', index=False)


