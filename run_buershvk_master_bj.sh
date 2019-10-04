#!/bin/bash

CUDA_VISIBLE_DIVICES=1  

python master_slaver.py \
  --region_path='./beijing_region.csv' \
  --result_path='./beijing_result.csv' \
  --succ_path='./beijing_succ.csv' \
  --isMaster=True \
  --key_words_path='./kw_level_1.txt'


#爬取url清单,未完全爬取，下一轮，放大覆盖 --region_path='./test_deyang_region.csv' \
#结果保存位置  --result_path='./test_deyang_result.csv' \
#切割n*ni,放大某个区域进行n*n的爬取  --cuts=2 \
#  --left=39.5 \
#  --right=39.51 \
#  --top=105.9 \
#  --down=105.91 \
#关键字段 --key_words_path='./kw.csv'

