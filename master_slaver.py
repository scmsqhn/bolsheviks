#!encoding=utf-8
# ================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: master_slaver.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-07-26
#   describe:
# ================================================================

"""
分布式进程
Reads: 61651
在Thread和Process中，应当优选Process，因为Process更稳定，而且，Process可以分布到多台机器上，而Thread最多只能分布到同一台机器的多个CPU上。

Python的multiprocessing模块不但支持多进程，其中managers子模块还支持把多进程分布到多台机器上。一个服务进程可以作为调度者，将任务分布到其他多个进程中，依靠网络通信。由于managers模块封装很好，不必了解网络通信的细节，就可以很容易地编写分布式多进程程序。

举个例子：如果我们已经有一个通过Queue通信的多进程程序在同一台机器上运行，现在，由于处理任务的进程任务繁重，希望把发送任务的进程和处理任务的进程分布到两台机器上。怎么用分布式进程实现？

原有的Queue可以继续使用，但是，通过managers模块把Queue通过网络暴露出去，就可以让其他机器的进程访问Queue了。

我们先看服务进程，服务进程负责启动Queue，把Queue注册到网络上，然后往Queue里面写入任务：
"""

"""
('merchant_info_beijing', "CREATE TABLE `merchant_info_beijing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL COMMENT '商户名称',
  `address` varchar(255) DEFAULT NULL COMMENT '商户地址',
  `latitude` varchar(255) DEFAULT NULL COMMENT '纬度',
  `longitude` varchar(255) DEFAULT NULL COMMENT '经度',
  `uid` varchar(255) DEFAULT NULL COMMENT '百度商户id',
  `telephone` varchar(255) DEFAULT NULL COMMENT '商户电话',
  `url` varchar(255) DEFAULT NULL,
  `province` varchar(255) DEFAULT NULL COMMENT '省份',
  `city` varchar(255) DEFAULT NULL COMMENT '城市',
  `keyword` varchar(255) DEFAULT NULL COMMENT '采集关键词',
  `district` varchar(255) DEFAULT NULL COMMENT '地区',
  `adcode` varchar(255) DEFAULT NULL,
  `street` varchar(255) DEFAULT NULL COMMENT '街道',
  `street_number` varchar(255) DEFAULT NULL COMMENT '街道号码',
  `tianyan_status` int(3) NOT NULL DEFAULT '0' COMMENT '天眼采集状态',
  `source` varchar(255) DEFAULT NULL,
  `tag` varchar(255) DEFAULT NULL COMMENT '百度标签',
  `type` varchar(255) DEFAULT NULL COMMENT '百度类别',
  `detail_url` varchar(255) DEFAULT NULL COMMENT '百度详情url',
  `transferLatitude` varchar(255) DEFAULT NULL COMMENT '转换后的纬度',
  `transferLongitude` varchar(255) DEFAULT NULL COMMENT '转换后的经度',
  `getNums` int(11) DEFAULT '0' COMMENT '获取次数(非采集字段fxz)',
  `locked` int(11) DEFAULT '0' COMMENT '乐观锁(非采集字段fxz)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_address` (`name`,`address`) USING BTREE,
  KEY `normal_index` (`transferLatitude`,`transferLongitude`,`getNums`,`locked`)
) ENGINE=InnoDB AUTO_INCREMENT=11920121 DEFAULT CHARSET=utf8")

        {
            "name":"小峰户外弹弓竞技俱乐部",
            "location":{
                "lat":39.322161,
                "lng":116.489124
            },
            "address":"金雀街28号附近",
            "province":"河北省",
            "city":"廊坊市",
            "area":"永清县",
            "street_id":"2f1a71e8a9d50448a20464e2",
            "telephone":"13931628999,18131697722",
            "detail":1,
            "uid":"2f1a71e8a9d50448a20464e2",
            "detail_info":{
                "tag":"运动健身;体育场馆",
                "type":"life",
                "detail_url":"http://api.map.baidu.com/place/detail?uid=2f1a71e8a9d50448a20464e2&output=html&source=placeapi_v2",
                "image_num":"3",
                "children":[

                ]
            }
        },
"""


# taskmanager.py
import re
import tensorflow as tf
import random, time, queue
import json
#from address_scan import gen_target_url as gen_target_url
import traceback
import time, sys, queue
import pdb
from multiprocessing.managers import BaseManager
#from address_scan import gen_target_url as gen_target_url
import sys
#import bolshevik2
#from bolshevik2.address_scan import gen_target_url
#sys.path.append('..')
import myflag
import address_scan
import mongohelper


server_addr = '192.168.1.65'
server_port= 8787
import myflag
FLAGS = myflag.FLAGS
# 从BaseManager继承的QueueManager:
import logging
tf.logging.set_verbosity(logging.INFO)
handlers = [
    logging.FileHandler('./main.log'),
]
logging.getLogger('tensorflow').handlers = handlers

if FLAGS.isMaster:
   class QueueManager(BaseManager):
       pass
   task_queue = queue.Queue()
   result_queue = queue.Queue()

   QueueManager.register('get_task_queue', callable=lambda: task_queue)
   QueueManager.register('get_result_queue', callable=lambda: result_queue)
   manager = QueueManager(address=(server_addr, 8999), authkey='abc'.encode('utf-8'))
   manager.start()
   task = manager.get_task_queue()
   result = manager.get_result_queue()

   with open(FLAGS.result_path,'a+') as gr:
       with open(FLAGS.succ_path,'a+') as gs:
           tf.logging.info('>>> 读取region_url')
           gen = address_scan.gen_target_url(FLAGS.region_path)
           tf.logging.info('>>> 读取url完毕')
           conn = mongohelper.MongoHelper('127.0.0.1',27017)
           tf.logging.info('>>> mongodb 连接完毕')
           while(1):
               url = ""
               try:
                   if task.qsize()<20:
                       for i in range(5):
                           url = gen.__next__()
                           url = re.sub('[\r\n ]',"",url)
                           tf.logging.info('分布式写入任务')
                           task.put(url)
               except StopIteration:
                   tf.logging.info('all the url push into the queue of task')
                   traceback.print_exc()
               try:
                   [ret,url] = result.get().split('&&&')
                   __ret__ = json.loads(ret)
                   __ret__['url'] = url
                   #__ret__ = {}
                   #for kv in ret:
                   #    if type(kv) == dict:
                   #        for k in kv:
                   #            __ret__[k] = kv[k]
                   #    elif type(kv) == str:
                   #        __ret__[kv] = ret[kv]
                   #    else:
                   #        tf.logging.info("no use of content")
                   #        tf.logging.info(kv)
                   #__ret__["url"] = url
                   item = json.dumps(__ret__,ensure_ascii=False)
                   gr.write(item+"\n")
                   gs.write(url+"\n")
                   oid = conn.insert(__ret__)
                   tf.logging.info("写入mongodb")
                   tf.logging.info(str(oid))
               except queue.Empty:
                   tf.logging.info('result queue is empty.')
                   traceback.print_exc()
               except:
                   tf.logging.info('预料外的错误')
                   traceback.print_exc()


if not FLAGS.isMaster:
    class QueueManager(BaseManager):
        pass
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')
    m = QueueManager(address=(server_addr, 8999), authkey='abc'.encode('utf-8'))
    m.connect()
    task = m.get_task_queue()
    result = m.get_result_queue()
    while(1):
        try:
            url = task.get(timeout=1)
            result.put(address_scan.fetch_one(url))
            tf.logging.info('fetch_one')
            tf.logging.info(url)
        except queue.Empty:
            tf.logging.info('task queue is empty.')
            traceback.print_exc()
        except:
            traceback.print_exc()
            result.put(address_scan.fetch_one(url))
            tf.logging.info('预料外的错误')

# 处理结束:
tf.logging.info('worker exit.')

"""
任务进程要通过网络连接到服务进程，所以要指定服务进程的IP。

现在，可以试试分布式进程的工作效果了。先启动taskmanager.py服务进程：
"""
