from booknlp.booknlp import BookNLP
import sys, re, os

model_params={
        # for name cloze, we just need the entity tagger
        "pipeline":"entity", 

        # but if you want to run all of booknlp over the book anyway, use this instead
        # "pipeline":"entity,quote,supersense,event,coref",

        "model":"small"
    }
    
booknlp=BookNLP("en", model_params)

input_folder=sys.argv[1] 
# output_id=sys.argv[2] # stella-edit: parse output_id from file instead

# with open(input_file) as file:
#         output_directory="booknlp_output/%s" % output_id 
#         booknlp.process(input_file, output_directory, output_id)

# Reversing folder order to see if can recover more books without error
files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
files.sort(reverse=True)

# Loop through txt files in folder
for filename in files:
    print(f"Currently trying {filename}")
# for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        output_id = filename[:-4]
        input_file_path = os.path.join(input_folder, filename)
        output_directory = "/home/stellajia/genai-copyright/non-libgen-exp/hathitrust_output/%s" % output_id
        if os.path.exists(output_directory):
            print(f"Output directory already exists for {output_id}. Skipping...")
            continue 
        # Open the file and run booknlp
        with open(input_file_path) as file:
            #output_directory = "booknlp_output_new/%s" % output_id 
            print("Processing", output_id)
            try:
                booknlp.process(input_file_path, output_directory, output_id)
            except Exception as e:
                print("Error in processsing file:", filename)
                print("Error details:", str(e))
            print("Finished processing ", output_id)
