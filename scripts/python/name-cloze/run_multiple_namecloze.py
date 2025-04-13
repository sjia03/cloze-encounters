
# Runs a shell script over multiple books located in the booknlp_output folder and outputs the name cloze for each book

import os 
import subprocess
import sys

booknlp_output_folder=sys.argv[1] 
shell_script = "/home/stellajia/genai-copyright/experiment/name-cloze-scripts/create_name_cloze.sh"

# book_folder represents the output_id which is the input of the shell script 
print("Folder of book: ", booknlp_output_folder)
for book_folder in os.listdir(booknlp_output_folder):
    if book_folder != ".DS_Store":
        book_folder = book_folder.replace(".txt", "")  # Remove .txt extension if it exists
        book_folder_path = os.path.join(booknlp_output_folder, book_folder)
        name_cloze_file = book_folder + ".name_cloze.txt"
        tokens_file = book_folder + ".tokens"
        entities_file = book_folder + ".entities"

        # Check if book folder exists
        if not os.path.isdir(book_folder_path):
            print(f"🚨 {book_folder} does not exist")
            # os.makedirs(book_folder_path)  # Create the book folder
            continue

        # Check if .name_cloze.txt file exists in the book folder
        if os.path.exists(os.path.join(book_folder_path, name_cloze_file)):
            print(f"🔆 Skipping {name_cloze_file} because exists")
            continue

        # Check if .tokens or .entities file exists
        if not (os.path.exists(os.path.join(book_folder_path, tokens_file)) or os.path.exists(os.path.join(book_folder_path, entities_file))):
            print(f"💥 .tokens or .entities file does not exist for {book_folder}")
            continue

        # If none of the above conditions are met, run the shell script
        print("Running shell script for:", book_folder)
        subprocess.run([shell_script, book_folder, booknlp_output_folder])
        print("✅ Generated name cloze for:", book_folder)