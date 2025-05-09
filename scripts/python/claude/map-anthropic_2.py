import csv
import json
import anthropic
import os

# Set up the Anthropic client
client = anthropic.Anthropic(api_key="ANTHROPIC_API_KEY")

# Paths to input files
input_csv_path = "/scratch/sxp8182/UCB/final_combined/batch_responses/batch_log.csv"
jsonl_directory = "/scratch/sxp8182/UCB/final_combined/booknlp_output_16k_jsonl"
output_directory = "/scratch/sxp8182/UCB/final_combined/output-anthropic"

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Function to process each batch and map custom_id to anthropic_id and text
def process_batches(input_csv_path):
    with open(input_csv_path, mode="r") as input_csv:
        reader = csv.reader(input_csv)
        
        # Iterate through each batch and JSONL file from the CSV
        for row in reader:
            batch_id, jsonl_file = row[0], row[1]
            jsonl_path = os.path.join(jsonl_directory, jsonl_file)
            output_csv_path = os.path.join(output_directory, jsonl_file.replace('.jsonl', '_mapping.csv'))
            
            # Check if output CSV already exists; if so, skip this file
            if os.path.exists(output_csv_path):
                print(f"Output file {output_csv_path} already exists. Skipping {jsonl_file}.")
                continue
            
            print(f"Processing batch {batch_id} for file {jsonl_file}")
            
            # Map custom_id to anthropic_id and text using batch results
            custom_to_anthropic_text = get_anthropic_mappings(batch_id)
            
            # Process the JSONL file and write to the new output CSV
            create_custom_id_mapping_csv(jsonl_path, output_csv_path, custom_to_anthropic_text)

# Function to get mappings of custom_id to anthropic_id and text from batch results
def get_anthropic_mappings(batch_id):
    custom_to_anthropic_text = {}
    try:
        # Fetch results from the batch
        for result in client.beta.messages.batches.results(batch_id):
            custom_id = result.custom_id
            text = ''.join([block.text for block in result.result.message.content])
            custom_to_anthropic_text[custom_id] = (custom_id, text)
    except Exception as e:
        print(f"Error fetching batch results for {batch_id}: {e}")
    return custom_to_anthropic_text

# Function to create CSV mapping custom_id to anthropic_id and text
def create_custom_id_mapping_csv(jsonl_path, output_csv_path, custom_to_anthropic_text):
    with open(jsonl_path, 'r') as jsonl_file, open(output_csv_path, mode="w", newline="") as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(["original_custom_id", "anthropic_id", "text"])  # Header for the output CSV
        
        # Read each line from JSONL and match custom_id with anthropic_id and text
        for line in jsonl_file:
            message = json.loads(line.strip())
            original_custom_id = message.get("custom_id")
            anthropic_id = message.get("anthropic_id")
            
            # Check if this custom_id has a mapping in the batch results
            if anthropic_id in custom_to_anthropic_text:
                anthropic_id, text = custom_to_anthropic_text[anthropic_id]
                writer.writerow([original_custom_id, anthropic_id, text])
    
    print(f"Mapping CSV created for {jsonl_path} at {output_csv_path}")

# Run the processing for the input CSV file
process_batches(input_csv_path)

print("All mappings have been saved to individual CSV files for each JSONL file.")
