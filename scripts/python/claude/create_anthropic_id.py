import os
import json
import re
import uuid

# Directory containing the jsonl files
jsonl_directory = '/scratch/sxp8182/UCB/final_combined/booknlp_output_16k_jsonl'

# Function to sanitize and truncate custom_id to meet Claude API requirements
def sanitize_custom_id(custom_id):
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    sanitized_custom_id = re.sub(r'[^a-zA-Z0-9_-]', '', custom_id)
    return sanitized_custom_id

# Function to generate anthropic_id by combining uuid and last 32 characters of custom_id
def generate_anthropic_id(custom_id):
    sanitized_custom_id = sanitize_custom_id(custom_id)
    
    # Take the last 32 characters of the sanitized custom_id
    truncated_custom_id = sanitized_custom_id[-20:]
    
    # Generate UUID
    unique_id = str(uuid.uuid4())
    
    # Combine UUID with the truncated custom_id to create anthropic_id
    anthropic_id = f"{unique_id}_{truncated_custom_id}"
    
    return anthropic_id

# Process each jsonl file in place
def process_jsonl_files(jsonl_directory):
    # Iterate through all JSONL files in the directory
    for jsonl_file in os.listdir(jsonl_directory):
        if jsonl_file.endswith('.jsonl'):
            file_path = os.path.join(jsonl_directory, jsonl_file)
            print(f"Processing file: {jsonl_file}")
            
            processed_entries = []
            
            # Read the JSONL file line by line
            with open(file_path, 'r') as infile:
                for line in infile:
                    entry = json.loads(line)
                    
                    # Generate anthropic_id (UUID + last 32 characters of sanitized custom_id)
                    entry['anthropic_id'] = generate_anthropic_id(entry['custom_id'])
                    
                    # Append the modified entry to processed entries
                    processed_entries.append(entry)
            
            # Write the processed entries back to the same file
            with open(file_path, 'w') as outfile:
                for entry in processed_entries:
                    outfile.write(json.dumps(entry) + '\n')
            
            print(f"Updated JSONL file in place: {file_path}")

# Call the function to process all JSONL files
process_jsonl_files(jsonl_directory)
