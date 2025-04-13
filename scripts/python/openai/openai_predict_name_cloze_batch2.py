from openai import OpenAI
import time
import json
import os

class OpenAIBatchProcessor:
    def __init__(self, api_key):
        client = OpenAI(api_key=api_key)
        self.client = client

    def process_batch(self, book_name, input_file_path, endpoint, completion_window):
        try:
            # Upload the input file
            with open(input_file_path, "rb") as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose="batch"
                )

            # Create the batch job
            batch_job = self.client.batches.create(
                input_file_id=uploaded_file.id,
                endpoint=endpoint,
                completion_window=completion_window,
                metadata={
                    "book_name": book_name
                }
            )
            print(f"✅ Sent {book_name} to batch")
            print("*" * 20)
            return True  # Indicating success

        except openai.error.OpenAIError as e:
            if '503' in str(e):
                print(f"503 error for {book_name}. Will retry.")
                return False  # Indicating failure
            else:
                print(f"❌ API Error: {str(e)}")
                raise

def is_jsonl_file_not_empty(file_path):
    # Check if the file exists and is not empty by size
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Check if there's at least one non-empty line
            for line in file:
                if line.strip():  # Check if the line is not just whitespace
                    return True
    return False

def save_processed_files(processed_files, file_path='processed_files.json'):
    with open(file_path, 'w') as f:
        json.dump(processed_files, f)

def load_processed_files(file_path='processed_files.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def retry_failed_batches(processor, failed_batches, endpoint, completion_window, retries=3):
    """Retry processing failed batches with exponential backoff."""
    for attempt in range(retries):
        print(f"Retry attempt {attempt + 1}...")
        still_failed = []
        for batch in failed_batches:
            book_name, input_file_path = batch
            result = processor.process_batch(book_name, input_file_path, endpoint, completion_window)
            if not result:
                still_failed.append(batch)
        if not still_failed:
            break
        failed_batches = still_failed
        time.sleep(2 ** attempt)  # Exponential backoff

# Loop through folder of books and call process_batch for each book in the folder
def process_all_jsonl_files_in_folder(processor, jsonl_folder_path, endpoint, completion_window):
    count = 1
    processed_files = load_processed_files()
    failed_batches = []

    for filename in os.listdir(jsonl_folder_path):
        if filename.endswith(".jsonl"):
            input_file_path = os.path.join(jsonl_folder_path, filename)
            book_name = filename[:-6]  # Remove '.jsonl'

            if book_name in processed_files:
                print(f"🔄 Skipping file {count}: {book_name} already processed.")
                print("*" * 20)
                count += 1
                continue

            if is_jsonl_file_not_empty(input_file_path):
                print(f"Processing file {count}: {input_file_path}")

                # Call the process_batch method on each JSONL file
                result = processor.process_batch(book_name, input_file_path, endpoint, completion_window)
                count += 1
                if result:
                    processed_files.append(book_name)
                    save_processed_files(processed_files)  # Update the file after each successful book
                else:
                    failed_batches.append((book_name, input_file_path))
            else:
                print(f"💥 Skipping empty file: {input_file_path}")
                print("*" * 20)


    # Retry failed batches with exponential backoff
    retry_failed_batches(processor, failed_batches, endpoint, completion_window)

    print("Processing of all JSONL files in folder complete.")

# Example usage
api_key = os.getenv("OPENAI_API_KEY") 
processor = OpenAIBatchProcessor(api_key)

# Process the batch job
jsonl_folder_path = "/home/stellajia/genai-copyright/experiment/booknlp_output_16k_jsonl"  # Path to your input JSONL file
endpoint = "/v1/chat/completions"
completion_window = "24h"

# Process the batch job
process_all_jsonl_files_in_folder(processor, jsonl_folder_path, endpoint, completion_window)
