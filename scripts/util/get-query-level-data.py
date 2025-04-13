#!/usr/bin/env python
# coding: utf-8

# ## get query level data
# 
# goal is to have a dataframe at the query level (to save space maybe book metadata will be in a separate file that can be mapped to the query level data). columns should have: 
# 
# - query_id
# - query 
# - book_title
# - mapfilename
# - correct_answer
# - gpt35_turbo_answer
# - gpt4o_answer
# - claude_answer
# - llama8b_answer
# - llama70b_answer
# - (and all book metadata)
# 

# In[3]:


import ast
import string
import os
import pandas as pd
import json
import csv
import re

os.chdir("/Users/stellajia/Dropbox/23.Copyright-LLMs")

# gpt3.5
gpt35_query_lvl_json = 'rawdata/model-output/gpt35-output.jsonl'
gpt35_query_lvl_csv = 'rawdata/model-output-clean/gpt35_query_lvl.csv'

# gpt4o
gpt4o_query_lvl_json = 'rawdata/model-output/gpt4o-output.jsonl'
gpt4o_query_lvl_csv = 'rawdata/model-output-clean/gpt4o_query_lvl.csv'
# claude
claude_folder = 'rawdata/model-output/claude-output'
claude_query_lvl_csv = 'rawdata/model-output-clean/claude_query_lvl.csv'

# llama 8b
## each book is stored as a CSV file
llama8b_folder = 'rawdata/model-output/llama-3.1-8B-output'
llama8b_query_lvl_csv = 'rawdata/model-output-clean/llama8b_query_lvl.csv'

# llama 70b
## each book is stored as a CSV file
llama70b_folder = 'rawdata/model-output/llama-3.1-70B-output'
llama70b_query_lvl_csv = 'rawdata/model-output-clean/llama70b_query_lvl.csv'

# gemini
## each book is stored as a folder with a jsonl file inside (repetitive)
## (raw output stored in gemini folder requires running map_correct_token.py and parse_gemini_results.py)
gemini_folder = 'rawdata/model-output/gemini-output'
gemini_file = 'rawdata/model-output/gemini-output.csv'
gemini_query_lvl_csv = 'rawdata/model-output-clean/gemini_query_lvl.csv'

def process_json_to_csv(json_file_path, csv_file_path, file_type="json"):
    """
    Converts a JSON or JSONL file to a CSV file.
    
    :param json_file_path: Path to the input JSON or JSONL file.
    :param csv_file_path: Path to the output CSV file.
    :param file_type: Either "json" for a standard JSON file or "jsonl" for a JSONL file.
    """
    # Ensure the file exists
    if not os.path.exists(json_file_path):
        print(f"Error: The file {json_file_path} does not exist.")
        return
    
    # Check if the file is empty
    if os.stat(json_file_path).st_size == 0:
        print(f"Error: The file {json_file_path} is empty.")
        return

    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        # Define CSV columns
        fieldnames = ['book_title', 'query_id', 'query', 'gpt_answer', 'correct_answer']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()  # Write header row

        n = 0  # Move n outside so it tracks across JSONL lines

        try:
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                if file_type == "json":  
                    # ✅ JSON File: Load entire file
                    data = json.load(json_file)  
                    n += process_data_to_csv(data, writer, n)

                elif file_type == "jsonl":  
                    # ✅ JSONL File: Read line by line
                    for line in json_file:
                        line = line.strip()
                        if line:  # Ignore empty lines
                            try:
                                data = json.loads(line)  # Load one JSON object per line
                                n += process_data_to_csv(data, writer, n)
                            except json.JSONDecodeError as e:
                                print(f"Skipping malformed JSONL line: {e}")
                else:
                    print(f"Error: Invalid file_type '{file_type}'. Use 'json' or 'jsonl'.")
                    return

            print(f"✅ Data successfully written to {csv_file_path}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

def process_data_to_csv(data, writer, n):
    """Processes JSON data and writes it to the CSV file."""
    count = 0  # Track books in this batch
    for book_title, passages in data.items():
        for passage_id, passage_data in passages.items():
            try:
                gpt_answer = passage_data['output']['response']
                correct_answer = passage_data['output']['correct']
                query = passage_data['input']['passage']

                writer.writerow({
                    'book_title': book_title,
                    'query_id': passage_id,
                    'query': query,
                    'gpt_answer': gpt_answer,
                    'correct_answer': correct_answer
                })
            except KeyError as e:
                print(f"⚠️ Missing key {e} in book {book_title}, passage {passage_id}")

        count += 1
        print(f"📚 {n + count}: {book_title} processed")  # Now increments properly
    
    return count  # Return how many books were processed

def merge_csv_files(input_folder: str, output_file: str):
    """
    Merges all non-empty CSV files in the given input folder into a single CSV file.
    
    Parameters:
        input_folder (str): Path to the folder containing CSV files.
        output_file (str): Path to save the merged CSV file.
    
    Each row in the merged CSV retains the source file name under "map_file_name".
    Skipped empty files are printed at the end.
    """
    all_dfs = []
    skipped_files = []
    n = 0

    for file in os.listdir(input_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(input_folder, file)
            
            if os.path.getsize(file_path) == 0:
                skipped_files.append(file)  # Store skipped files
                print(f"Skipping empty file: {file}")
                continue  # Skip empty files
            
            df = pd.read_csv(file_path)

            n += 1
            df["map_file_name"] = file  # Add column to store file name
            all_dfs.append(df)
            print(f"{n}: {file} processed")

    # Concatenate all dataframes
    if all_dfs:
        merged_df = pd.concat(all_dfs, ignore_index=True)
        merged_df.to_csv(output_file, index=False)
        print(f"Merged CSV saved as {output_file}")
    else:
        print("No non-empty CSV files found in the folder.")

    # Print skipped files
    if skipped_files:
        print(f"Skipped {len(skipped_files)} empty files: {skipped_files}")


# GPT35
process_json_to_csv(gpt35_query_lvl_json, gpt35_query_lvl_csv, "jsonl")
gpt35_query_lvl_df = pd.read_csv(gpt35_query_lvl_csv)
# remove duplicates (fetching batch script will overestimate amount of books to collect--keep first duplicate)
gpt35_query_lvl_df = gpt35_query_lvl_df.drop_duplicates(subset='query_id', keep='first')
gpt35_query_lvl_df = gpt35_query_lvl_df.rename(columns={'gpt_answer': 'gpt35_answer'})
gpt35_query_lvl_df.to_csv(gpt35_query_lvl_csv, index=False)


# GPT4O
process_json_to_csv(gpt4o_query_lvl_json, gpt4o_query_lvl_csv)
gpt4o_query_lvl_df = pd.read_csv(gpt4o_query_lvl_csv)
gpt4o_query_lvl_df = gpt4o_query_lvl_df.rename(columns={'gpt_answer': 'gpt4o_answer'})
gpt4o_query_lvl_df.to_csv(gpt4o_query_lvl_csv, index=False)

# Llama 8b
merge_csv_files(llama8b_folder, llama8b_query_lvl_csv)
llama_8b_df = pd.read_csv(llama8b_query_lvl_csv)
llama_8b_df['map_file_name'] = llama_8b_df['map_file_name'].str.replace('.csv', '') 
llama_8b_df = llama_8b_df.rename(columns={'final_output': 'llama8b_answer'})
llama_8b_df = llama_8b_df.rename(columns={'custom_id': 'query_id'})
llama_8b_df.to_csv(llama8b_query_lvl_csv, index=False)


# Llama 70b
merge_csv_files(llama70b_folder, llama70b_query_lvl_csv)
llama_70b_df = pd.read_csv(llama70b_query_lvl_csv)
llama_70b_df['map_file_name'] = llama_70b_df['map_file_name'].str.replace('.csv', '')
llama_70b_df = llama_70b_df.rename(columns={'final_output': 'llama70b_answer'})
llama_70b_df = llama_70b_df.rename(columns={'custom_id': 'query_id'})
llama_70b_df.to_csv(llama70b_query_lvl_csv, index=False)


# Claude
merge_csv_files(claude_folder, claude_query_lvl_csv)
claude_df = pd.read_csv(claude_query_lvl_csv)
claude_df['map_file_name'] = claude_df['map_file_name'].str.replace('.csv', '') 
claude_df = claude_df.rename(columns={'original_custom_id': 'query_id'})
claude_df = claude_df.rename(columns={'text': 'claude_answer'})
claude_df.to_csv(claude_query_lvl_csv, index=False)


# Gemini 
gemini_df = pd.read_csv(gemini_file)
gemini_df = gemini_df.rename(columns={'passage': 'query'})
gemini_df = gemini_df.rename(columns={'gemini_token': 'gemini_answer'})
gemini_df = gemini_df.rename(columns={'original_filename': 'book_title'})
gemini_df['query'] = gemini_df['query'].str.slice(0, -12) # remove the "\n Output:" from query
gemini_df = gemini_df[gemini_df['gemini_answer'].notna()]
gemini_df = gemini_df.drop_duplicates(subset='query', keep='first')
gemini_df.to_csv('rawdata/model-output-clean/gemini_query_lvl.csv', index=False)


# Merge all data together ----------------------------------------------------------------
# Load data
gpt35_query_lvl_df = pd.read_csv('rawdata/model-output-clean/gpt35_query_lvl.csv')
gpt4o_query_lvl_df = pd.read_csv('rawdata/model-output-clean/gpt4o_query_lvl.csv')
llama_8b_df = pd.read_csv('rawdata/model-output-clean/llama_output_8b_query_lvl.csv')
llama_70b_df = pd.read_csv('rawdata/model-output-clean/llama_output_70b_query_lvl.csv')
claude_df = pd.read_csv('rawdata/model-output-clean/claude_query_lvl.csv')
gemini_df = pd.read_csv('rawdata/model-output-clean/gemini_query_lvl.csv')

# Merge data
merged_df = pd.merge(gpt35_query_lvl_df, gpt4o_query_lvl_df, on='query', how='left')
merged_df = merged_df.drop(columns=['query_id_x', 'correct_answer_x'])
merged_df = merged_df.rename(columns={'query_id_y': 'query_id'})
merged_df = merged_df.rename(columns={'correct_answer_y': 'correct_answer'})
merged_df = pd.merge(merged_df, llama_8b_df, on='query_id', how='left')
merged_df = pd.merge(merged_df, llama_70b_df, on='query_id', how='left')
merged_df = pd.merge(merged_df, claude_df, on='query_id', how='left')
merged_df = pd.merge(merged_df, gemini_df, on='query', how='left')

# Clean merged data
print("Original shape: ", merged_df.shape)

merged_df = merged_df[['book_title_y', 'query_id', 'query','map_file_name', 'gpt35_answer', 'gpt4o_answer', 'llama8b_answer', 'llama70b_answer', 'claude_answer', 'gemini_answer', 'correct_answer']]
merged_df = merged_df.rename(columns={'book_title_y': 'book_title'})
merged_df = merged_df[merged_df['correct_answer'].notna()]
merged_df = merged_df[merged_df['gemini_answer'].notna()]
merged_df = merged_df[merged_df['llama8b_answer'].notna()]
merged_df = merged_df.drop_duplicates(subset='query_id', keep='first')
print(f"After removing duplicates: {merged_df.shape}")

## take out <name>, <\nname>, </name> from answers write function 
def clean_answers(answer):
    if isinstance(answer, str):
        # Regular expression to match text inside <word></word> tags
        answer = re.sub(r'</?[^>]+>', '', answer)
        answer = answer.lower()
    return answer

merged_df['gpt35_answer'] = merged_df['gpt35_answer'].apply(clean_answers)
merged_df['gpt4o_answer'] = merged_df['gpt4o_answer'].apply(clean_answers)
merged_df['llama8b_answer'] = merged_df['llama8b_answer'].apply(clean_answers)
merged_df['llama70b_answer'] = merged_df['llama70b_answer'].apply(clean_answers)
merged_df['claude_answer'] = merged_df['claude_answer'].apply(clean_answers)
merged_df['gemini_answer'] = merged_df['gemini_answer'].apply(clean_answers)
merged_df['correct_answer'] = merged_df['correct_answer'].apply(clean_answers)

# remove all punctuation from map_file_name
translator = str.maketrans('', '', string.punctuation + " ")
merged_df['map_file_name'] = merged_df['map_file_name'].apply(lambda x: x.translate(translator))
merged_df['map_file_name'] = merged_df['map_file_name'].str.replace('mapping', '')
merged_df.tail(2)

# Map query level data to book metadata ----------------------------------------------------------------

query_lvl_df = merged_df
book_lvl_df = pd.read_csv('rawdata/isbndb-goodreads.csv')
book_lvl_df = book_lvl_df.rename(columns={'file_name': 'map_file_name'})

# merge by map_file_name
merged_df = pd.merge(query_lvl_df, book_lvl_df, on='map_file_name', how='left')

# keep main columns
merged_df = merged_df[['book_title', 'query_id', 'query', 'map_file_name', 'gpt35_answer', 'gpt4o_answer', 'llama8b_answer', 'llama70b_answer', 'claude_answer', 'gemini_answer', 'correct_answer', 'in_books3', 'num_reviews', 'num_ratings', 
                       'avg_rating', 'genres', 'goodreads_year', 'author',
                       'isbn13', 'isbn10_v2', 'isbn13_v2']]
# remove in_books3 is none
merged_df = merged_df[merged_df['in_books3'].notna()]
# remove pub_year -1
merged_df = merged_df[merged_df['goodreads_year'] != -1]
# rename goodreads_year to pub_year
merged_df = merged_df.rename(columns={'goodreads_year': 'pub_year'})

merged_df = merged_df[merged_df['gpt35_answer'].notna()]
merged_df = merged_df[merged_df['gpt4o_answer'].notna()]
merged_df = merged_df[merged_df['llama8b_answer'].notna()]
merged_df = merged_df[merged_df['llama70b_answer'].notna()]
merged_df = merged_df[merged_df['claude_answer'].notna()]
merged_df = merged_df[merged_df['gemini_answer'].notna()]
merged_df = merged_df[merged_df['correct_answer'].notna()]
merged_df = merged_df.rename(columns={'map_file_name': 'book_id'})

merged_df.to_csv('filedata/query-level-final.csv', index=False)


