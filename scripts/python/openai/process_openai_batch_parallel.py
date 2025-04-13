import time
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from openai import OpenAI, RateLimitError

# SET UP ----------------------

api_key = os.getenv("OPENAI_API_KEY") 

# Assuming OpenAI client is already imported
client = OpenAI(api_key=api_key)

lock = threading.Lock()  # Ensure thread-safe access to shared resources

def extract_input_content(text):
    start_index = text.rfind("Input: ") + len("Input: ")
    end_index = text.rfind("Output:")
    return text[start_index:end_index].strip()

def process_output_file(text_file, book_name, combined_data_local):
    text_file = text_file.strip().split("\n")
    
    # Create a dictionary to hold the updates for this file
    updates = {}

    for line in text_file:
        data = json.loads(line.strip())
        custom_id = data["custom_id"]
        correct_answer = data["custom_id"].split('-')[-2] if data["custom_id"].count('-') >= 2 else None

        # Check if the custom_id is already present in the local combined_data
        if custom_id not in combined_data_local[book_name]:
            updates[custom_id] = {"output": {}, "input": {}}

        # If there's already an output, skip this custom_id
        elif combined_data_local[book_name][custom_id]["output"]:
            continue 

        # Update the local dictionary with output details
        updates[custom_id] = {
            "output": {
                "batch_id": data["id"],
                "response": data["response"]["body"]["choices"][0]["message"]["content"],
                "correct": correct_answer
            },
            "input": combined_data_local[book_name].get(custom_id, {}).get("input", {})
        }

    # Apply the updates to the local combined_data
    combined_data_local[book_name].update(updates)


def process_input_file(input_file_path, book_name, combined_data_local):
    with open(input_file_path, "r") as file:
        # Create a dictionary to hold the updates for this file
        updates = {}
        
        for line in file:
            data = json.loads(line.strip())
            custom_id = data["custom_id"]
            
            # Check if the custom_id is already present in the local combined_data
            if custom_id not in combined_data_local[book_name]:
                updates[custom_id] = {"output": {}, "input": {}}

            # If there's already an input, skip this custom_id
            elif combined_data_local[book_name][custom_id]["input"]:
                continue 

            # Extract the input content and update the local dictionary
            input_prompt = data.get("body", {}).get("messages", [])[0].get("content", "")
            extracted_passage = extract_input_content(input_prompt)

            updates[custom_id] = {
                "output": combined_data_local[book_name].get(custom_id, {}).get("output", {}),
                "input": {
                    "passage": extracted_passage
                }
            }

        # Apply the updates to the local combined_data
        combined_data_local[book_name].update(updates)

# Thread-safe function to save files
def save_data_to_file(path, data):
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

# Takes in a batch and saves the content into output
def process_batch(batch, combined_data_local, batch_dict_local):
    batch_id = batch.id
    book_name = batch.metadata.get('book_name', 'Unknown')

    try:
        output_file_id = client.batches.retrieve(batch_id).output_file_id
    except RateLimitError as e:
        time.sleep(60)
        output_file_id = client.batches.retrieve(batch_id).output_file_id

    # Initialize local dictionaries to store per-thread results
    combined_data_local[book_name] = combined_data_local.get(book_name, {})

    if output_file_id:
        file_response = client.files.content(output_file_id).text
        process_output_file(file_response, book_name, combined_data_local)

        input_file_path = f"/home/stellajia/genai-copyright/experiment/booknlp_output_16k_jsonl/{book_name}.jsonl"
        process_input_file(input_file_path, book_name, combined_data_local)

    # Add local batch info (no lock here since it's local to this thread)
    batch_dict_local[batch_id] = {
        "book_name": book_name,
        "output_file_id": output_file_id
    }

    print(f"Finished processing book: {book_name}")

def save_final_data(global_combined_data, global_batch_dict, all_combined_data, all_batch_dicts):
    # Merge the data from all threads safely here
    for book_name, data in all_combined_data.items():
        if book_name not in global_combined_data:
            global_combined_data[book_name] = data
        else:
            global_combined_data[book_name].update(data)

    global_batch_dict.update(all_batch_dicts)
    
    # Save to files with the lock to prevent race conditions
    save_data_to_file(combined_data_local_path, global_combined_data)
    save_data_to_file(output_batch_dict_path, global_batch_dict)

# Main function to handle batch retrieval
def fetch_batches(after_token):
    count_batch_sets = 0
    count_mapped_book = len(batch_dict)

    # Start retrieving batches
    while count_batch_sets * batches_per_request < total_batches_to_retrieve:
        try:
            # after_token = list(batch_dict.keys())[-1] if batch_dict else None
            response = client.batches.list(limit=batches_per_request, after=after_token)
            if not response.data:
                break
            
            batches = response.data
            count_batch_sets += 1
            # Local data to store batch results for this set of threads
            thread_combined_data = {}
            thread_batch_dicts = {}

            print(f"Retrieved batch set {count_batch_sets}, ending on {after_token}...")

            # Parallelize processing of batches
            with ThreadPoolExecutor(max_workers=10) as executor:
                
                try: 
                    futures = [executor.submit(process_batch, batch, thread_combined_data, thread_batch_dicts) for batch in batches]
                    
                except Exception as e:
                    print(f"Error fetching batches: {e}")

            save_final_data(combined_data, batch_dict, thread_combined_data, thread_batch_dicts)
            print(f"Finished processing batch set and saved {count_batch_sets}")
            print("*"*20)
            after_token = batches[-1].id if batches else None

        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}. Waiting for 60 seconds before retrying...")
            time.sleep(60)
            
        
    
# LOAD AND RUN ------------

# Load combined_data and batch_dict which stores data locally
combined_data_local_path = '/home/stellajia/genai-copyright/experiment/output_combined_data3_parallel.jsonl'
if os.path.exists(combined_data_local_path):
    with open(combined_data_local_path, 'r', encoding='utf-8') as file:
        combined_data = json.load(file)
else:
    combined_data = {}

output_batch_dict_path = "/home/stellajia/genai-copyright/experiment/otuput_id_name_mapping3_parallel.jsonl"
if os.path.exists(output_batch_dict_path):
    with open(output_batch_dict_path, 'r', encoding='utf-8') as file:
        batch_dict = json.load(file)
else:
    batch_dict = {}

# Pagination after token
total_batches_to_retrieve = 8000
batches_per_request = 50
after_token = list(batch_dict.keys())[-1] if batch_dict else None

print(f"Saved {len(batch_dict)} to lagged map")
print(f"Saved {len(combined_data)} OpenAI output")
print(f"Beginning on {after_token}")

start_time = time.time()
# Start the process
fetch_batches(after_token)
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Script took {elapsed_time:.2f} seconds to run.")
print("Finished retrieving and processing all batches.")