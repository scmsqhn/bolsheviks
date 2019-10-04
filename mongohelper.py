#!/encoding=utf-8
#================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: mongo_helper.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-05-15
#   describe: a interface of mongodb
#================================================================

import pandas as pd
import sys
import json
import os
import pdb
import traceback
import pymongo
import tensorflow as tf
import time
import os


class MongoHelper():

    def __init__(self,host,port):
        self.client = pymongo.MongoClient(host,port)
        tf.logging.info('>>> new a mongo client %s %s'%(host,port))
        """
        baidu_poi = databases name
        """
        self.db_name = 'baidu_poi'# this is create in mongo
        self.db_name = 'bj_poi'# this is create in mongo

    def __str__(self):
        return self.name

    def __all__(self):
        return [self.insert,self.search,self.insert_csv]

    def insert(self, kv):
        try:
            return self.client.db_name.coll.insert(kv)
        except:
            traceback.print_exc()

    def search(self, kv):
        '''
        kv = {filed_name: value}
        '''
        try:
            return self.client.db_name.coll.find(kv)
        except:
            traceback.print_exc()

    """
    def insert_csv(self,filepath):
        try:
            assert filepath[-3:]=='csv'
        except:
            tf.logging.info('>>> it must be a csv file')
            tf.logging.info(filepath)
        lines = open(filepath,'r').readlines()
        for line in lines:
          try:
            style = line.split(',')[0]
            time = line.split(',')[1]
            content = line.split(',')[2:]
            kv = {}
            kv['style'] = style
            kv['time'] = time
            kv['content'] = content
          except:
              traceback.print_exc()
    """
def backData(is_save=True):
        """
        back data the mongodb
        """
        DBUSER='myadmin'        #用户
        DBPASS='redhat'           #密码
        IP='127.0.0.1'        #主机
        DATA_DIR='/home/siy/mongo_data/tmp'           #目录
        PATH_DUMP='/usr/bin/mongodump'    #命令路径
        BACKITEMS=["%s -h %s:27017 -o %s" % (PATH_DUMP,IP,DATA_DIR)]
        #BACKITEMS=["%s -h %s:27017 -u %s -p %s -o %s" % (PATH_DUMP,IP,DBUSER,DBPASS,DATA_DIR)]
        if not is_save:
            PATH_RES='/usr/local/mongodb/bin/mongorestore'
            BACKITEMS=["%s -h %s:27017 --dir %s" % (PATH_RES,IP,DATA_DIR)]
        try:
            for item in BACKITEMS:
                print (item)
                #print (os.system(item))
        except RuntimeError:
            import traceback
            traceback.print_exc()

def read_csv_sort_uniq(filepath):
    res_set = set()
    filename = open(filepath,'r')
    lines = filename.readlines()
    for line in lines:
        kv = json.loads(line)
        if not kv.get('results',False):
            res_set.add(line)
        else:
            for results in json.loads(line):
                for result in results['results']:
                    res_set.add(json.dumps(result,ensure_ascii=False))
    return res_set

if __name__=="__main__":
    #backData(False)
    #pdb.set_trace()
    #res_set = read_csv_sort_uniq("address_output.csv")
    #pdb.set_trace()

    g = open('total_address.json','w')
    gb = open('total_address_wb.json','w')
    mMongoClient = MongoHelper("127.0.0.1",27017)
    results = mMongoClient.search({})
    json_output = {}
    json_output['version'] = 'mongodb_address_0806'
    json_output['data'] = []
    cnt=0
    while(1):
        if cnt%10000==1:
            df = pd.DataFrame(json_output['data'])
            g = open('total_address_%s.csv'%cnt,'w')
            df.to_csv(g)
            del json_output
            json_output = {}
            json_output['version'] = 'mongodb_address_0806'
            json_output['data'] = []
        result = results.next()
        url = None
        try:
            url = result['url']
            print(url)
        except:
            pass
            #print('there is no url here')
        try:
            for result in result['results']:
                item = {}
                for k in result:
                    item[k] = result[k]
                if not None:
                    item['url'] = url
                json_output['data'].append(item)
        except KeyError:
            item = {}
            for k in result:
                item[k] = result[k]
            if not None:
                item['url'] = url
            json_output['data'].append(item)
        cnt+=1
    json.dump(json_output,g)
    #json.dump(json_output,gb)

