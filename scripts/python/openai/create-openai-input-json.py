import os
import random
import json
import re

def create_input_jsonl(book_folder_path, jsonl_file_path):
    
    text_template = """
    You have seen the following passage in your training data. \\
    What is the proper name that fills in the [MASK] token in it? \\
    This name is exactly one word long, and is a proper name (not \\
    a pronoun or any other word). You will be penalized if you predict pronouns like him, he, she, us, etc. Please predict only proper nouns! \\
    You must make a guess, even if you are uncertain.
    
    Example:
    Input: "Stay gold, [MASK], stay gold."
    Output: <name>Ponyboy</name>

    Input: "The door opened, and [MASK], dressed and hatted, entered with a cup of tea."
    Output: <name>Gerty</name>

    Input: %s
    Output:
    """
    request_count = 1
    with open(jsonl_file_path, 'w') as jsonl_file:
        
        for filename in os.listdir(book_folder_path):
        
                if filename.endswith(".name_cloze.txt"):
                    input_file_path = os.path.join(book_folder_path, filename)
                    book_name = clean_text(filename[:-15])
                    
                    with open(input_file_path, 'r') as input_file:
                        lines = input_file.readlines()
                        random_lines = random.sample(lines, min(100, len(lines)))
                        
                        for line in random_lines:
                            columns = line.strip().split('\t')
                            masked_passage = clean_text(columns[-1])
                        
                            correct = clean_text(columns[-2])
                        
                            
                            json_data = {
                                "custom_id": f"{book_name}-{correct}-{request_count}",
                                "method": "POST",
                                "url": "/v1/chat/completions",
                                "body": {
                                    "model": "gpt-3.5-turbo",
                                    "messages": [
                                        {"role": "user", "content": text_template % masked_passage}
                                    ],
                                    "max_tokens": 1000
                                }
                            }
                            
                            # Write JSON object to JSONL file
                            jsonl_file.write(json.dumps(json_data) + '\n')
                            request_count += 1 
                            print(f"Finished writing {book_name}")

def clean_text(text):
    # Option 1: Remove all non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Option 2: Replace common Unicode sequences (optional)
    # text = text.replace('\u2019', "'").replace('\u2013', "-")  # Add other replacements as needed

    return text                            
                            
# Loop through all books and turn name_cloze.txt into .jsonl

def process_all_books(all_books_folder_path):
    for book_name in os.listdir(all_books_folder_path):
        input_file_path = os.path.join(all_books_folder_path, book_name)
        
        if len(book_name) > 150:
            book_name = book_name[:150]
        json_file_path = f"booknlp_output_16k_jsonl/{book_name}.jsonl"
        create_input_jsonl(input_file_path, json_file_path)
        

# Example usage:
process_all_books("/home/stellajia/genai-copyright/experiment/booknlp_output_16k")
