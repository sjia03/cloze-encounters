#!/usr/bin/bash

job_count=0
for folder in /home/stellajia/genai-copyright/experiment/booknlp_output_16k/parent_folder_*; do
    if [ -d "$folder" ]; then
        job_name="${folder##*/}"
        bsub   -u stellajia@berkeley.edu -L /usr/bin/bash -J "$job_name" -n 1 -e "${job_name}.err" -o "${job_name}.out" <<EOF 
        #!/usr/bin/bash
        #####source /apps/anaconda3/etc/profile.d/conda.sh
        #####conda activate booknlp
        #source ~/.bashrc
        chmod 750 create_name_cloze.sh
        cd /home/stellajia/genai-copyright/experiment
        /home/stellajia/.conda/envs/booknlp/bin/python run_multiple_namecloze.py "$folder"
EOF
        ((job_count++))
        echo "Submitted job for $job_name"
        sleep 1  # Add a small delay between submissions
    fi
done

echo "Total jobs submitted: $job_count"
