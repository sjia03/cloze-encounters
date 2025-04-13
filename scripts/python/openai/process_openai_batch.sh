#!/usr/bin/bash
#BSUB -n 1
#BSUB -e %J.err
#BSUB -o %J.out
#BSUB -u stellajia@berkeley.edu  # Email notification address
#BSUB -N                        # Send email when job is finished

source /apps/anaconda3/etc/profile.d/conda.sh
conda activate booknlp
cd /home/stellajia/genai-copyright/experiment
/home/stellajia/.conda/envs/booknlp/bin/python /home/stellajia/genai-copyright/experiment/name-cloze-scripts/process_openai_batch3.py

