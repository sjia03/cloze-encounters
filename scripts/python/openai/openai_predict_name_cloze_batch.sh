#!/usr/bin/bash
#BSUB -n 1
#BSUB -e %J.err
#BSUB -o %J.out


source /apps/anaconda3/etc/profile.d/conda.sh
conda activate booknlp
cd /home/stellajia/genai-copyright/experiment
/home/stellajia/.conda/envs/booknlp/bin/python /home/stellajia/genai-copyright/experiment/name-cloze-scripts/openai_predict_name_cloze_batch2.py 
