# Map each passage from gemini results to custom_id so can figure out correct token
# Do this by finding the corresponding jsonl file for that book in the booknlp_output_16k_jsonl folder

import os
import json
import pandas as pd
import unicodedata

# File paths
scraped_results_file = "/home/stellajia/genai-copyright/experiment/gemini/scraped_results_14k.csv"
filename_mapping_file = "/home/stellajia/genai-copyright/experiment/gemini/filename_mappings.csv"
booknlp_folder = "/home/stellajia/genai-copyright/experiment/booknlp_output_16k_jsonl"
output_file = "scraped_results_with_custom_id_14k.csv"

# Load filename mapping
map_df = pd.read_csv(filename_mapping_file)
map_df["new_filename"] = map_df["new_filename"].str.replace(".jsonl", "", regex=False)

# Load scraped results
scraped_df = pd.read_csv(scraped_results_file)

# Add new columns if it doesn't exist!!
# Ensure 'custom_id' column exists
if "custom_id" not in scraped_df.columns:
    scraped_df["custom_id"] = None
# Ensure 'correct_token' column exists
if "correct_token" not in scraped_df.columns:
    scraped_df["correct_token"] = None
# Ensure 'original_filename' column exists
if "original_filename" not in scraped_df.columns:
    scraped_df["original_filename"] = None

# Function to process each row
def process_row(row):
    try:
        # print("Processing row: ", row.get('subfolder_name', 'Unknown'))
        subfolder_name = row["subfolder_name"]
        
        # Ensure 'passage' is a string; handle NaN or non-string cases
        passage = row["passage"]
        if pd.isna(passage) or not isinstance(passage, str):
            print(f"Invalid or missing passage for subfolder: {subfolder_name}")
            return [None, None, None]
        
        passage = passage.replace(" ", "").lower()

        # Find the corresponding original filename
        mapping_row = map_df.loc[map_df["new_filename"] == subfolder_name]
        if mapping_row.empty:
            print(f"No mapping found for {subfolder_name}")
            return [None, None, None]

        original_filename = mapping_row["original_filename"].values[0]
        original_filename = unicodedata.normalize('NFC', original_filename)
        jsonl_path = os.path.join(booknlp_folder, original_filename)

        if not os.path.exists(jsonl_path):
            print(f"File not found: {jsonl_path}")
            return [None, None, original_filename]

        with open(jsonl_path, mode="r", encoding="utf-8") as jsonl_file:
            for line in jsonl_file:
                data = json.loads(line)
                jsonl_passage = data.get("body", {}).get("messages", [{}])[0].get("content", "").split("Input:")[-1].replace(" ", "").lower().strip()

                if jsonl_passage == passage:
                    custom_id = data.get("custom_id", None)
                    correct_token = None
                    if custom_id:
                        parts = custom_id.split('-')
                        correct_token = parts[-2] if parts[-1].isdigit() else parts[-1]
                    # print(f"Processed file: {original_filename}")
                    return [custom_id, correct_token, original_filename]
    except Exception as e:
        print(f"Error processing row: {row.get('subfolder_name', 'Unknown')}, Error: {e}")

    return [None, None, original_filename]

# Apply the processing function to each row
# Filter rows where 'custom_id' is None
processed_rows = scraped_df[scraped_df["custom_id"].isnull()]
print("Number of rows to process: ", processed_rows.shape[0])

# Apply the process_row function only to the filtered rows
processed_rows[["custom_id", "correct_token", "original_filename"]] = processed_rows.apply(lambda row: pd.Series(process_row(row)), axis=1)
processed_file = "processed_rows.csv"
processed_rows.to_csv(processed_file, index=False, encoding="utf-8")
print(f"Processed rows saved to {processed_file}.")

# Update the original dataframe with the processed rows
scraped_df.loc[scraped_df["custom_id"].isnull(), ["custom_id", "correct_token", "original_filename"]] = processed_rows

# Save the updated DataFrame to a new CSV
scraped_df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Updated results saved to {output_file}.")
