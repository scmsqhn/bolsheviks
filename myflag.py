#!encoding=utf-8
# ================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: myflag.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-07-26
#   describe:
# ================================================================

import tensorflow as tf
flags = tf.flags
FLAGS = flags.FLAGS

flags.DEFINE_string(
    "key_words_path", './kw_uniq.txt',"key_words_path.")

flags.DEFINE_string(
    "region_path", "./bj_region_uniq.csv","region_path.")

flags.DEFINE_string(
    "result_path", "./bj_poi_uniq.csv","result_path.")

flags.DEFINE_string(
    "succ_path", "./succ_url_uniq.txt","result_path.")

flags.DEFINE_float(
    "left", 30.484349,"left.")

flags.DEFINE_float(
    "right", 31.734286,"right.")

flags.DEFINE_float(
    "top", 103.851681,"top.")

flags.DEFINE_float(
    "down", 105.121315,"down.")

flags.DEFINE_integer(
    "cuts", 2, "down.")

flags.DEFINE_bool(
    "isMaster", True,"boolen.")
