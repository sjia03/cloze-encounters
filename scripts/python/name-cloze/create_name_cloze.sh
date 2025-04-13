#!/bin/bash
# filename=$1
output_id=$1
all_book_folder=$2

# run BookNLP to tokenize the text and extract entities
# python run_booknlp.py $filename $output_id

# create name cloze examples from those BookNLP files
# python create_name_cloze_from_booknlp.py booknlp_output/$output_id/$output_id.entities booknlp_output/$output_id/$output_id.tokens > booknlp_output/$output_id/$output_id.name_cloze.txt
# /home/stellajia/.conda/envs/booknlp/bin/python create_name_cloze_from_booknlp.py $all_book_folder/$output_id/$output_id.entities $all_book_folder/$output_id/$output_id.tokens > $all_book_folder/$output_id/$output_id.name_cloze.txt
/home/stellajia/.conda/envs/booknlp/bin/python create_name_cloze_from_booknlp.py $all_book_folder/$output_id/$output_id.entities $all_book_folder/$output_id/$output_id.tokens $all_book_folder/$output_id/$output_id.name_cloze.txt

# ---

# # Directory where books are 
# BOOKS_DIR="/Users/stellajia/Desktop/Professional/data-innovation-lab/generate_name_cloze/input_done"
# # BOOKS_DIR = "/input_done"
# # Directory where processed BookNLP books are
# OUTPUT_DIR="/Users/stellajia/Desktop/Professional/data-innovation-lab/generate_name_cloze/booknlp_output"
# # OUTPUT_DIR = "/booknlp_output"


# for book_file in "$BOOKS_DIR"/*; do
#     # Extract the base name of the file for use in output paths
#     output_id=$(basename "$book_file" .txt) # Assuming the files are .txt; adjust as needed
#     echo "Name of file: $book_file" 
#     # TODO: if really wanted to can run booknlp process here

#     # Run the Python script for each book
#     python create_name_cloze_from_booknlp.py "$OUTPUT_DIR/$output_id/$output_id.entities" "$OUTPUT_DIR/$output_id/$output_id.tokens" > "$OUTPUT_DIR/$output_id/$output_id.name_cloze.txt"
# done


# echo "All books processed."
