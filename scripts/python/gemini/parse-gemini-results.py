# Takes folder of gemini output and outputs a csv with the following columns:
# subfolder_name, passage, gemini_response, log_prob, gemini_token

import os
import json
import csv
import re

# Define the main folder
main_folder = "/home/stellajia/genai-copyright/experiment/gemini/gemini_all"
output_csv = "/home/stellajia/genai-copyright/experiment/gemini/scraped_results_14k.csv"

def extract_gemini_token(response):
    """
    Extract the token based on the conditions:
    1. If the string contains <name>, extract the content between <name> and </name>.
    2. If the string is a single word, return it.
    3. If the string contains more than one word, return None.
    """
    # Check if <name> exists in the string
    name_match = re.search(r'<name>(.*?)</name>', response)
    if name_match:
        # Return the content between <name> and </name>
        return name_match.group(1)
    elif len(response.split()) == 1:
        # If there's only one word, return it
        return response
    else:
        # For strings with more than one word, return None
        return None

# Create the CSV file and write the headers
with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["subfolder_name", "passage", "gemini_response", "log_prob", "gemini_token"])
    
# Iterate through each subfolder
for subfolder in os.listdir(main_folder):
    subfolder_path = os.path.join(main_folder, subfolder)

    if os.path.isdir(subfolder_path):
        # Locate the predictions.jsonl file in the nested folder
        nested_folder = next((
            os.path.join(subfolder_path, subdir)
            for subdir in os.listdir(subfolder_path)
            if os.path.isdir(os.path.join(subfolder_path, subdir))
        ), None)

        if nested_folder:
            predictions_file = os.path.join(nested_folder, "predictions.jsonl")

            if os.path.exists(predictions_file):
                with open(predictions_file, mode="r", encoding="utf-8") as file:
                    for line in file:
                        try:
                            # Parse the JSON line
                            data = json.loads(line)

                            # Extract relevant fields
                            passage_full = data.get("request", {}).get("contents", [{}])[0].get("parts", [{}])[0].get("text", "")
                            # Extract text after the final "Input:"
                            passage = passage_full.split("Input:")[-1].strip()
                            gemini_response = data.get("response", {}).get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            log_prob = data.get("response", {}).get("candidates", [{}])[0].get("avgLogprobs", None)
                            
                            # Calculate gemini_token
                            gemini_token = extract_gemini_token(gemini_response)

                            # Write to CSV
                            with open(output_csv, mode="a", newline="", encoding="utf-8") as csv_file:
                                writer = csv.writer(csv_file)
                                writer.writerow([subfolder, passage, gemini_response, log_prob, gemini_token])

                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in subfolder {subfolder}: {e}")
                        except Exception as e:
                            print(f"Unexpected error in subfolder {subfolder}: {e}")
    
print(f"Scraping completed. Results saved to {output_csv}.")
