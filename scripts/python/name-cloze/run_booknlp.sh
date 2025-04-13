#!/usr/bin/bash
#BSUB -n 1
#BSUB -e %J.err
#BSUB -o %J.out
source /apps/anaconda3/etc/profile.d/conda.sh
conda activate booknlp
cd /home/stellajia/genai-copyright/experiment
python run_booknlp.py input-16k
