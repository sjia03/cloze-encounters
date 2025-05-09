import os
import json
import csv
import anthropic
from datetime import datetime
from anthropic.types.beta.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.beta.messages.batch_create_params import Request

# Set up the Anthropic client
client = anthropic.Anthropic(api_key="ANTHROPIC_API_KEY")

# Directory containing the JSONL files
jsonl_directory = '/scratch/sxp8182/UCB/final_combined/booknlp_output_16k_jsonl'
# Directory where batch response metadata will be saved
response_directory = '/scratch/sxp8182/UCB/final_combined/batch_responses'
# Path to the CSV file for logging batch IDs and JSONL filenames
csv_log_path = os.path.join(response_directory, "batch_log.csv")

# Ensure response directory exists
os.makedirs(response_directory, exist_ok=True)

# Function to create requests from a list of messages
def create_requests(messages):
    requests = []
    for message in messages:
        request = Request(
            custom_id=message["anthropic_id"],
            params=MessageCreateParamsNonStreaming(
                model="claude-3-haiku-20240307",
                max_tokens=25,
                messages=message["body"]["messages"]
            )
        )
        requests.append(request)
    return requests

# Function to process each JSONL file
def process_jsonl_file(file_path):
    messages = []
    with open(file_path, 'r') as f:
        for line in f:
            message = json.loads(line.strip())
            messages.append(message)
    return messages

# Process each JSONL file independently and send batch requests
def process_all_files(jsonl_directory):
    all_files = [f for f in os.listdir(jsonl_directory) if f.endswith('.jsonl')]
    
    # Ensure the CSV log file exists and has headers
    initialize_csv_log()
    
    # Load already processed files from the log
    processed_files = load_processed_files()
    
    for jsonl_file in all_files:
        # Skip already processed files
        if jsonl_file in processed_files:
            print(f"Skipping already processed file: {jsonl_file}")
            continue
        
        file_path = os.path.join(jsonl_directory, jsonl_file)
        print(f"Processing file: {jsonl_file}")
        
        # Read the JSONL file and extract messages
        messages = process_jsonl_file(file_path)
        
        # Skip if there are no messages in the file
        if len(messages) < 1:
            print(f"Skipping empty file: {jsonl_file}")
            continue
        
        # Send batch request for the messages from the current file, passing the filename
        send_batch_request(messages, jsonl_file)

# Function to send batch request to the Claude API and store the response metadata
def send_batch_request(messages, jsonl_file):
    print(f"Sending batch request with {len(messages)} messages...")
    
    requests = create_requests(messages)
    
    response = client.beta.messages.batches.create(
        requests=requests
    )
    print(f"Batch request sent successfully! Batch ID: {response.id}")
    
    # Save the response metadata to a file, including the filename
    save_response_metadata(response, jsonl_file)
    
    # Log the batch ID and JSONL filename in CSV
    log_batch_to_csv(response.id, jsonl_file)

# Function to save the response metadata
def save_response_metadata(response, jsonl_file):
    batch_id = response.id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"batch_response_{batch_id}_{timestamp}.json"
    file_path = os.path.join(response_directory, file_name)
    
    # Prepare the metadata dictionary to save as JSON
    metadata = {
        "jsonl_file": jsonl_file,
        "id": response.id,
        "type": response.type,
        "processing_status": response.processing_status,
        "request_counts": {
            "processing": response.request_counts.processing,
            "succeeded": response.request_counts.succeeded,
            "errored": response.request_counts.errored,
            "canceled": response.request_counts.canceled,
            "expired": response.request_counts.expired
        },
        "created_at": response.created_at.isoformat(),
        "expires_at": response.expires_at.isoformat(),
        "ended_at": response.ended_at.isoformat() if response.ended_at else None,
        "archived_at": response.archived_at.isoformat() if response.archived_at else None,
        "cancel_initiated_at": response.cancel_initiated_at.isoformat() if response.cancel_initiated_at else None,
        "results_url": response.results_url
    }
    
    # Write the response metadata to a file
    with open(file_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    print(f"Response metadata saved to {file_path}")

# Initialize the CSV log file with headers if it doesn't already exist
def initialize_csv_log():
    if not os.path.exists(csv_log_path):
        with open(csv_log_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Batch ID", "JSONL Filename"])

# Log the batch ID and JSONL filename to CSV
def log_batch_to_csv(batch_id, jsonl_file):
    with open(csv_log_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([batch_id, jsonl_file])
    print(f"Logged batch ID {batch_id} and JSONL file {jsonl_file} to CSV.")

# Load already processed files from the log
def load_processed_files():
    processed_files = set()
    if os.path.exists(csv_log_path):
        with open(csv_log_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)  # Skip the header row
            for row in reader:
                if row:
                    processed_files.add(row[1])  # Add JSONL filename to the set
    return processed_files

# Call the function to process all files and send batch requests
process_all_files(jsonl_directory)



# print(client.beta.messages.batches.list(
#     limit=2
# ))

# Call the function to process all files and send batch requests
#process_all_files(jsonl_directory)

# count = 0
# for result in client.beta.messages.batches.results(
#     "msgbatch_01LKtQFQxtuFdKnaeimsg64w",
# ):
#     print(result)
#     count+=1
#     if count > 5:
#         break

# client.beta.messages.batches.cancel(
#     "msgbatch_01JDZYFqTcy8ab941QNh1Ywy",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_01JSuwhE1He7WDGu5JPt7bDL",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_01Q88qhC8mTewoGHpwjengQr",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_01WkwoYP9FdSx44M2oaBre6g",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_01WkxrrRncpNcKQ1Ke4bx2gE",
# )

# client.beta.messages.batches.cancel(
#     "msgbatch_01XJ4Ue1dv26wgUyT4njqyaB",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_014BrTDbToWyzRaZQQ342gNj",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_014uFPvJoM9SxQ56XHH7QrqA",
# )
# client.beta.messages.batches.cancel(
#     "msgbatch_014zxvdV4D7Svoia4nJoUfmo",
# )
