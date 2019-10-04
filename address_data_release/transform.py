#!/encoding=utf-8
# ================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: transform.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-07-31
#   describe:
# ================================================================
import json

def json_2_file():                                                     |~
"""
json 转成需要的任何格式
"""
    g = open('new.txt','w+')                                           |~
    addrs = json.load(open('addrs.json','r'))                          |~
    for addr in addrs:                                                 |~
        if addr == None:                                               |~
            continue                                                   |~
        try:                                                           |~
            if addr['city']=='北京市':                                 |~
                g.write("%s,%s\n"%(addr['name'],addr['address']))      |~
        except KeyError:                                               |~
            print(addr)                                                |~
            g.write("%s,%s\n"%(addr['name'],addr['name']))             |~
    g.close()
