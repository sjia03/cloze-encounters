#!/usr/bin/bash
#BSUB -n 1
#BSUB -e %J.err
#BSUB -o %J.out
source /apps/anaconda3/etc/profile.d/conda.sh
chmod 750 create_name_cloze.sh
conda activate booknlp
cd /home/stellajia/genai-copyright/experiment
python run_multiple_namecloze.py booknlp_output_16k