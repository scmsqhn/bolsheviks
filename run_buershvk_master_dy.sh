#!/bin/bash

CUDA_VISIBLE_DIVICES=1  

python master_slaver.py \
  --region_path='./deyang_region.csv' \
  --result_path='./deyang_result.csv' \
  --succ_path='./deyang_succ.csv' \
  --isMaster=True \
  --key_words_path='./kw_level_1.txt'

