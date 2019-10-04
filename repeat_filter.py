#!encoding=utf-8

# ================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: repeat_filter.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-07-19
#   describe:
# ================================================================

import pymysql
import os
import pickle
import traceback
import pdb
import json
import re
#==========
#北京
user = "user_baidumap"
password = "lqh4kwHnfm5&iinnzGdl"
host = "117.107.241.65"
port = 3306
database = "datacenter_baidumap"
#=========

def connect_test():
    #db = pymysql.connect(host,user,password,database)
    db = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=database,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print ("Database version : %s " % data)
    db.close()


def connect():
    """
    connect to db of address
    """
    db = pymysql.connect(host,user,password,database)
    cursor = db.cursor()
    return cursor,db

def execute(cursor,cmd):
    """
    execute a sql cmd
    """
    cursor.execute(cmd)
    return cursor

def combine(fp):
    total_res = []
    gen = os.walk(fp)
    for ii in gen:
      for i in ii[2]:
        print(i)
        print(os.path.join(fp,i))
        with open(os.path.join(fp,i),'rb') as g:
            try:
                res = pickle.load(g)
                res = json.loads(res)
                for k in res:
                    total_res.append(res[k])
            except:
                traceback.print_exc()
    return total_res

def write_into(total_res):
    with open('address.csv','w') as g:
      cnt=0
      for key in total_res:
        item = json.loads(key)
        lng = item['addr']['raw']['location']['lng']
        lat = item['addr']['raw']['location']['lat']
        name = item['addr']['raw']['formatted_address']
        address = item['addr']['raw']['sematic_description']
        g.write("%s,%s,%s,%s,%s\n"%(cnt,lng,lat,name,address))

def is_repeat(cursor, k,v):
    cmd = 'select * from merchant_info_beijing where %s="%s";'%(k,v)
    return execute(cursor, cmd)

import mongohelper


def check_from_file_2_mongo():
    diff_file = open("./diff_royal.txt","a+")
    from_file = open("./merge_u.txt","r")
    lines = from_file.readlines()
    mMongoClient = mongohelper.MongoHelper("127.0.0.1",27017)
    totalcnt, samecnt = 0, 0
    flag=True
    for line in lines:
        #name = re.sub('[\r\n ]','',line.split(',')[2])
        #address = re.sub('[\r\n ]','',line.split(',')[3])
        line = line.split(',')
        name = re.sub('[\r\n ]','',line[0])
        address = re.sub('[\r\n ]','',line[1])
        #url = re.sub('[\r\n ]','',line[2])
        print(name,address)
        #print(is_repeat(cursor, name,address))
        for i in mMongoClient.search({"address":address,"name":name}):
            samecnt+=1
            flag=False
            break
        totalcnt+=1
        if flag:
            print(line)
        print(samecnt)
        diff_file.write("%s,%s,%s\n"%(str(totalcnt),str(samecnt),line))
        diff_file.write("========================================\n")
        flag=True
    diff_file.close()
    from_file.close()

def mongo2file():
    f = open('mongo_filter.txt','w+')
    mMongoClient = mongohelper.MongoHelper("127.0.0.1",27017)
    for i in mMongoClient.search({"city":"北京市"}):
        f.write("%s,%s\n"%(i['name'],i['address']))
    f.close()

def check_position():
    diff_file = open("./diff_royal.txt","a+")
    #mMongoClient.insert_data_into_mongo()
    connect_test()
    cursor,db = connect()
    cmd = "show create table merchant_info_beijing;"
    cursor = execute(cursor,cmd)
    print(cursor.fetchone())
    cmd = "select * from merchant_info_beijing where city='北京市' limit 1;"
    cursor = execute(cursor,cmd)
    print(cursor.fetchone())
    cmd = "select name,address,url from merchant_info_beijing where city='北京市' limit 109;"
    cursor = execute(cursor,cmd)
    #with open("/home/siy/bolshevik2/bj_poi_total_0727.txt","r") as g:
    mMongoClient = mongohelper.MongoHelper("127.0.0.1",27017)
    totalcnt, samecnt = 0, 0
    flag=True
    while(1):
        line = cursor.fetchone()
        #name = re.sub('[\r\n ]','',line.split(',')[2])
        #address = re.sub('[\r\n ]','',line.split(',')[3])
        name = re.sub('[\r\n ]','',line[0])
        address = re.sub('[\r\n ]','',line[1])
        url = re.sub('[\r\n ]','',line[2])
        print(name,address)
        #print(is_repeat(cursor, name,address))
        for i in mMongoClient.search({"address":address,"name":name}):
            samecnt+=1
            flag=False
            break
        totalcnt+=1
        if flag:
            print(url)
            pdb.set_trace()
        print(samecnt)
        diff_file.write("%s,%s,%s\n"%(str(totalcnt),str(samecnt),line))
        diff_file.write("========================================\n")
        pdb.set_trace()
        flag=True
    diff_file.close()

def save_mysql_2_file():
    f = open('old.txt','a+')
    cursor,db = connect()
    cmd = "select name,address from merchant_info_beijing where city='北京市';"
    cursor = execute(cursor,cmd)
    while(1):
        line = cursor.fetchone()
        if line == None:
            continue
        name = re.sub('[\r\n ]','',line[0])
        address = re.sub('[\r\n ]','',line[1])
        f.write("%s,%s\n"%(name,address))

def json_2_file():
    g = open('new.txt','w+')
    addrs = json.load(open('addrs.json','r'))
    for addr in addrs:
        if addr == None:
            continue
        try:
            if addr['city']=='北京市':
                g.write("%s,%s\n"%(addr['name'],addr['address']))
        except KeyError:
            print(addr)
            g.write("%s,%s\n"%(addr['name'],addr['name']))
    g.close()

def check_defense():
    #mMongoClient = mongohelper.MongoHelper("127.0.0.1",27017)
    #mMongoClient.insert_data_into_mongo()
    connect_test()
    cursor,db = connect()
    #print(execute(cursor,"show create table merchant_info_beijing;"))
    cmd = "select * from merchant_info_beijing where city='北京市' limit 1000;"
    results = execute(cursor,cmd)
    print(results)
    with open("/home/siy/bolshevik2/bj_poi_total_0727.txt","r") as g:
        for line in g.readlines():
                name = line.split(',')[-2]
                address = line.split(',')[-1]
                if "北京" == address[:2]:
                    print(name,address)
                    print(is_repeat(cursor, "address", address))
                    print('========================================')

if __name__ == "__main__":
    #save_mysql_2_file()
    mongo2file()
    #json_2_file()
    #check_defense()
    #check_from_file_2_mongo()
    #check_position()

    #print(execute(cursor,cmd))
    """
    import pickle
    import json
    fp = '39.26_41.03_115.25_117.3_60_address.pkl'
    with open(fp,'rb') as g:
        res = pickle.load(g)
        res = json.loads(res)
        print(len(res))
        print(res)
    """
    #res = combine('/home/siy/buershvk')
    #write_into(res)
    pdb.set_trace()

