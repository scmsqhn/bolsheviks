#!encoding=utf-8
# ================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: address_scan.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-07-19
#   describe:
# ================================================================

import geocoder
import numpy as np
import pickle
import json
from mongohelper import MongoHelper
import json
#BAIDU_KEY = 'qpTylUQOllhr9GLyVp4c2dynWdTFGMhq'
#BAIDU_KEY = 'FDeyfZ18tRjFluQlZSNDsCpdePuniBKS'
BAIDU_KEYS = ['atm9tuqgfm5yvoGhLAKbXdGFFN65qBKo',\
'Wyf3ThiLhdvVSMwQP1LNUtwZ2PBmVq8X',\
'7RPBIHiACZWGAmGdCk5402NBW8odlImy',\
'1GBlMw0fwBSfjsCndnCoVvGtZZp4FI10',\
'K8ruiU1tS7h0HcjwsYOS9doepov0ut8V',\
'WHQCy16YRcco51zjELSsafWWWvwcxg7Z',\
'Vmc19Yd2IftC99WOXyU5MEdPcX1SCK9j',\
'DSeYRtoC8c90W6eonxosnnntwcuOUNZr',\
'cphYtCZhUz1vOkkU8sZU5GRVOtX0tqtB',\
'WwtD8z0nF5OIUp96DsrfTLI9GhpW51Ui']


global BAIDU_KEY

import pdb
import tensorflow as tf
tf.logging.set_verbosity(tf.logging.INFO)
import traceback
import time
import re

"""
configer
"""
#flags = master_slaver.flags
import myflag
FLAGS = myflag.FLAGS
## Required parameters

global URL_MASK
URL_MASK = 0


def encrypt(gg_lat,gg_lon):
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    x = gg_lon
    y = gg_lat
    z = np.sqrt(x * x + y * y) + 0.00002 * np.sin(y * x_pi)
    theta = np.math.atan2(y, x) + 0.000003 * np.cos(x * x_pi)
    bd_lon = z * np.cos(theta) + 0.0065
    bd_lat = z * np.sin(theta) + 0.006
    return bd_lat,bd_lon

def decrypt(bd_lat,bd_lon):
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = np.sqrt(x * x + y * y) - 0.00002 * np.sin(y * x_pi)
    theta = np.math.atan2(y, x) - 0.000003 * np.cos(x * x_pi)
    gg_lon = z * np.cos(theta)
    gg_lat = z * np.sin(theta)
    return gg_lat, gg_lon



def random_key():
    #print(BAIDU_KEYS[np.random.randint(len(BAIDU_KEYS))])
    return BAIDU_KEYS[np.random.randint(len(BAIDU_KEYS))]

BAIDU_KEY = random_key()

def format_addr(addr):
    """
    XY查询点位
    """
    addrdict = {}
    addrdict['addr'] = addr.__dict__['_list'][0].__dict__
    addrdict['X'] = addr.__dict__['location'][0]
    addrdict['Y'] = addr.__dict__['location'][1]
    #print(addrdict)
    return json.dumps(addrdict,ensure_ascii=False)


def rad(left,right,down,top,rows=1,cols=2):
    """
    left,right,top,down 经纬度坐标的左右上下
    rows,cols 行列
    在特定范围内，随机取出一地址
    """
    width = right-left
    height = top-down
    rad_array = np.random.rand(1,2)
    X = left+width*rad_array[0][0]
    Y = down+height*rad_array[0][1]
    try:
        assert X<=right
        assert X>=left
        assert Y<=top
        assert Y>=down
    except AssertionError:
        print("*** position is out of direction, pls check ***)")
        print(left,right,down,top,X,Y)
        pdb.set_trace()
    return (X,Y)

def address_pick(left,right,top,down,rows,cols):
    (X,Y) = rad(left,right,top,down,rows,cols)
    try:
        g = geocoder.baidu([X,Y], method='reverse',key=BAIDU_KEY)
        #print(g)
        return format_addr(g)
    except:
        return -1

def seq_address_pick(left,right,top,down,cnt,times):
    dx = right-left
    dx = dx/times
    dy = top-down
    dy = dy/times

    _x = cnt%times
    _y = cnt//times
    try:
        g = geocoder.baidu([left+_x*dx,down+_y*dy], method='reverse',key=BAIDU_KEY)
        print(g)
        return format_addr(g)
    except:
        return -1

def address_scan(left,right,top,down,cnt,repeat):
    res = {}
    for index in range(cnt, repeat*repeat):
        g = seq_address_pick(left,right,top,down,index,repeat)
        if g == -1:
            break
        res[str(len(res))] = g
    #print('len(res)', len(res))
    #print('cnt', cnt)
    #print('+cnt', len(res)+cnt)
    #print('+cnt', len(res)+cnt)
    cnt = cnt+len(res)
    return (json.dumps(res), cnt)

def api_test(X,Y):
    g = geocoder.baidu([X,Y], method='reverse',key=BAIDU_KEY)
    print(g.json)


import requests

def is_white(url):
    with open('succ_url.txt','r') as g:
        for i in g.readlines():
            if url in i:
                return True
    return False


def region_total(query,l,d,r,t,page_num=0):
    global BAIDU_KEY
    try:
        response = "None"
        while(1):
            url = "http://api.map.baidu.com/place/v2/search?scope=2&query=%s&bounds=%s,%s,%s,%s&scope=2&output=json&ak=%s&page_size=20&page_num=%s"%(query,l,d,r,t,BAIDU_KEY,page_num)
            response = requests.get(url)
            ret = json.loads(response.text)
            print(response.text)
            if ret['status']==0:
                break
            BAIDU_KEY = random_key()
        if ret['total']>399:
            print('需要继续拆分')
            print('total is more than 400, %s'%ret['total'])
            w = (l+r)/2
            h = (d+t)/2
            region_total(query,l,d,w,h,page_num)
            region_total(query,w,h,r,t,page_num)
            region_total(query,w,d,r,h,page_num)
            region_total(query,l,h,w,t,page_num)
        elif ret['total']>20:
            if r-l>0.1:
                w = (l+r)/2
                region_total(query,l,d,w,t,page_num)
                region_total(query,w,d,r,t,page_num)
            elif t-d>0.1:
                h = (d+t)/2
                region_total(query,l,d,r,h,page_num)
                region_total(query,l,h,r,t,page_num)
            else:
                l-=0.001
                r+=0.001
                d-=0.001
                t+=0.001
                print('可用urls')
                with open(FLAGS.region_path,'a+') as g:
                    page_nums = (ret['total']//20)+1
                    for page_num in range(0,page_nums):
                        url = "http://api.map.baidu.com/place/v2/search?scope=2&query=%s&bounds=%s,%s,%s,%s&output=json&ak=%s&page_size=20&page_num=%s"%(query,l,d,r,t,BAIDU_KEY,page_num)
                        g.write(url+'\n')
        elif ret['total']>0:
            if r-l>0.1:
                w = (l+r)/2
                region_total(query,l,d,w,t,page_num)
                region_total(query,w,d,r,t,page_num)
            elif t-d>0.1:
                h = (d+t)/2
                region_total(query,l,d,r,h,page_num)
                region_total(query,l,h,r,t,page_num)
            else:
                print('可用url')
                l-=0.001
                r+=0.001
                d-=0.001
                t+=0.001
                url = "http://api.map.baidu.com/place/v2/search?scope=2&query=%s&bounds=%s,%s,%s,%s&output=json&ak=%s&page_size=20&page_num=%s"%(query,l,d,r,t,BAIDU_KEY,page_num)
                with open(FLAGS.region_path,'a+') as g:
                    g.write(url+'\n')
        else:
            print('无用的接口')
    except TimeoutError:
        traceback.print_exc()
        region_total(query,l,d,r,t,page_num=0)
    except:
        traceback.print_exc()
        region_total(query,l,d,r,t,page_num=0)

def fetch_one(url):
    tf.logging.info('>>> feitch url')
    tf.logging.info(url)
    global BAIDU_KEY
    response = "None"
    while(1):
        try:
            response = requests.get(url)
            ret = json.loads(response.text)
            if ret['status']==0:
                break
            BAIDU_KEY = random_key()
            bk = re.findall(".+?ak=(.+?)&.+?",url)[0]
            url = re.sub(bk,BAIDU_KEY,url)
            tf.logging.info('>>> 更换url中的ak')
            tf.logging.info(url)
        except:
            BAIDU_KEY = random_key()
            bk = re.findall(".+?ak=(.+?)&.+?",url)[0]
            url = re.sub(bk,BAIDU_KEY,url)
            traceback.print_exc()
    return response.text+"&&&"+url
    #ret = json.loads(response.text)

    #return ret


def ret_query_scan(query,l,d,r,t,cnt,times,page_num,flag):
    global BAIDU_KEY
    dx = r-l
    dx = dx/times
    dy = t-d
    dy = dy/times
    _x = cnt%times
    _y = cnt//times
    _l = l+dx*_x
    _r = l+dx*(_x+1)
    _d = d+dy*_y
    _t = d+dy*(_y+1)
    #print(_l,_r,_d,_t)
    url = "http://api.map.baidu.com/place/v2/search?scope=2&query=%s&bounds=%s,%s,%s,%s&scope=2&output=json&ak=%s&page_size=20&page_num=%s"%(query,_l,_d,_r,_t,BAIDU_KEY,page_num)
    lines = []
    print(url)
    if is_white(url):
        print('重复页面,跳过')
        return lines
    try:
        response = requests.get(url)
        print(response.text)
        ret = json.loads(response.text)
        if ret['message']=="天配额超限，限制访问":
            BAIDU_KEY = random_key()
            with open(FLAGS.region_path,'a+') as g:
                g.write(url+"\n")
            print('baidu_key错误')
        elif ret['total']>399 and flag==True:
            print('total is more than 20, %s'%ret['total'])
            with open(FLAGS.region_path,'a+') as g:
                g.write(url+"\n")
            print('继续2x2切割')
        elif ret['total']>20 and flag==True:
            for dct in ret['results']:
                #print(dct)
                #pdb.set_trace()
                lat = dct['location']['lat']
                lng = dct['location']['lng']
                address = dct['address']
                name = dct['name']
                lines.append("%s,%s,%s,%s,\n"%(lat,lng,name,address))
            page_nums = (ret['total']//20)+1
            for page_num in range(1,page_nums):
                __lines = ret_query_scan(query,l,d,r,t,cnt,times,page_num,False)
                try:
                    assert len(__lines)>0
                except:
                    print('疑似重复页面')
                lines.extend(__lines)
        else:
            for dct in ret['results']:
                #print(dct)
                #pdb.set_trace()
                lat = dct['location']['lat']
                lng = dct['location']['lng']
                address = dct['address']
                name = dct['name']
                lines.append("%s,%s,%s,%s,\n"%(lat,lng,name,address))
            with open('succ_url.txt','a+') as g:
                g.write(url+'\n')
        return lines
    except:
        traceback.print_exc()
        return -1

def repeat_scan(filepath,URL_MASK):
    res = []
    with open(filepath, 'r') as g:
        #print(filepath)
        lines = g.readlines()
        lines = lines[URL_MASK:]
        for line in lines:
            if is_white(line):
                continue
            try:
                #print(line)
                query = re.findall(".+query=(.+?)&bounds.+",line)[0]
                region = re.findall(".+bounds=(.+?)&output.+",line)[0]
                #print((query, [float(i) for i in region.split(",")]))
                res.append([query, [float(i) for i in region.split(",")]])
            except:
                traceback.print_exc()
                pdb.set_trace()
    return res


def scan_first(L,R,D,T,key_words):
    cnt = 0
    fp = FLAGS.result_path
    #fp = "%s_%s_%s_%s_"%(L,R,T,D) + str(int(cnt)) + '_address.csv'
    #fp = "%s_%s_%s_%s_"%(L,R,T,D) + str(int(cnt)) + '_address.csv'
    while(1):
      if cnt>FLAGS.cuts*FLAGS.cuts:
        break
      print('>>> 初始cnt',cnt)
      for word in key_words:
        print(word)
        lines = ret_query_scan(word,L,D,R,T,cnt,FLAGS.cuts,0,True)
        print(lines)
        if lines == -1:
            continue
        else:
            with open(fp,'a+') as g:
                for line in lines:
                    print(line)
                    g.write(line)
      cnt+=1


def scan_first(L,R,D,T,key_words):
    cnt = 0
    fp = FLAGS.result_path
    #fp = "%s_%s_%s_%s_"%(L,R,T,D) + str(int(cnt)) + '_address.csv'
    #fp = "%s_%s_%s_%s_"%(L,R,T,D) + str(int(cnt)) + '_address.csv'
    while(1):
      if cnt>FLAGS.cuts*FLAGS.cuts:
        break
      print('>>> 初始cnt',cnt)
      for word in key_words:
        lines = ret_query_scan(word,L,D,R,T,cnt,FLAGS.cuts,0,True)
        print(lines)
        if lines == -1:
            continue
        else:
            with open(fp,'a+') as g:
                for line in lines:
                    print(line)
                    g.write(line)
      cnt+=1

def spyder():
    global URL_MASK
    '''
    PRJ='CQ'
    L,R,D,T = 39.26,41.03,115.25,117.30
    '''
    key_words = [line.strip() for line in open('kw.txt').readlines()]
    scan_first(FLAGS.left,FLAGS.right,FLAGS.down,FLAGS.top,key_words)
    BAIDU_KEY = random_key()
    while(1):
        lines = []
        with open(FLAGS.region_path,'r') as g:
            lines = g.readlines()
        if len(lines)-URL_MASK==0:
            print('>>> 没有新增,空白区域,无须爬取')
            break
        print('>>> 开始爬取')
        srcs = repeat_scan(FLAGS.region_path,URL_MASK)
        URL_MASK = len(lines)
        for src in srcs:
            key_words = [src[0]]
            L,D,R,T = src[1]
            scan_first(L,R,D,T,key_words)
    print('>>> 结束')

def gen_target_url(filepath):
    with open(FLAGS.region_path,'r') as fl:
        tf.logging.info('>>> 打开文件region_path')
        regions = fl.readlines()
        tf.logging.info('>>> 生成generate')
        for region in regions:
            yield region

if __name__ == "__main__":
    """
    fetch all url
    """
    BAIDU_KEY = random_key()
    key_words = [line.strip() for line in open(FLAGS.key_words_path).readlines()[-4:]]
    l,r,d,t = FLAGS.left,FLAGS.right,FLAGS.down,FLAGS.top
    for query in key_words:
        region_total(query,l,d,r,t,page_num=0)

    """
    fetch all result
    """

    """
    with open(FLAGS.result_path,'a+') as gr:
        with open(FLAGS.succ_path,'a+') as gs:
            tf.logging.info('>>> 读取region_url')
            gen = address_scan.gen_target_url(FLAGS.region_path)
            tf.logging.info('>>> 读取url完毕')
            conn = MongoHelper('127.0.0.1',27017)
            tf.logging.info('>>> mongodb 连接完毕')
            for url in gen:
                url = re.sub('[\r\n ]','',url)
                ret = fetch_one(url)
                for dct in ret['results']:
                    lat = dct['location']['lat']
                    lng = dct['location']['lng']
                    address = dct['address']
                    name = dct['name']
                    type = re.findall(".+?query=(.+?)&.+?",url)[0]
                    line = ("%s,%s,%s,%s,%s\n"%(lat,lng,name,address,type))
                    gr.write(line+"\n")
                gs.write(url+"\n")
                for item in ret['results']:
                    response = conn.insert(item)
                    tf.logging.info("写入mongodb")
                    tf.logging.info(item)
                    tf.logging.info(response)
    """

