#coding=utf8

import models
import sys
from info import * 

def gen_cache(cache_type=None):
    if cache_type is None  or cache_type not in [DISPLAY_DP , DISPLAY_WORDCOUNT , DISPLAY_CRF] :
        print >> sys.stderr ,  "A cached type should be specified : [ " ,
        print ",".join([DISPLAY_DP , DISPLAY_WORDCOUNT , DISPLAY_CRF]) + " ]"
        return -1

    print "begin to gen cache : " + cache_type 
    
    kinds = ["fruit","food","drink","wine","tea","all"]
    sexs = ["man","woman",""]
    times = ["morning","noon","afternoon","evening",""]
    provinces = ["北京".decode('utf-8'),
                    "浙江".decode('utf-8'),
                    "天津".decode('utf-8'),
                    "安徽".decode('utf-8'),
                    "上海".decode('utf-8'),
                    "福建".decode('utf-8'),
                    "重庆".decode('utf-8'),
                    "江西".decode('utf-8'),
                    "山东".decode('utf-8'),
                    "河南".decode('utf-8'),
                    "湖北".decode('utf-8'),
                    "湖南".decode('utf-8'),
                    "广东".decode('utf-8'),
                    "海南".decode('utf-8'),
                    "山西".decode('utf-8'),
                    "青海".decode('utf-8'),
                    "江苏".decode('utf-8'),
                    "辽宁".decode('utf-8'),
                    "吉林".decode('utf-8'),
                    "台湾".decode('utf-8'),
                    "河北".decode('utf-8'),
                    "贵州".decode('utf-8'),
                    "四川".decode('utf-8'),
                    "云南".decode('utf-8'),
                    "陕西".decode('utf-8'),
                    "甘肃".decode('utf-8'),
                    "黑龙江".decode('utf-8'),
                    "香港".decode('utf-8'),
                    "澳门".decode('utf-8'),
                    "广西".decode('utf-8'),
                    "宁夏".decode('utf-8'),
                    "新疆".decode('utf-8'),
                    "内蒙古".decode('utf-8'),
                    "西藏".decode('utf-8'),
                    ""]
    for province in provinces:
        for sex in sexs:
            for time in times:
                for kind in kinds:
                    result = models.cal_pmi(kind,sex,time,province , cache_type)
                    print "add cache sex:%s time:%s province:%s kind:%s cache_type:%s"%(sex,time,province,kind,cache_type)
               
    print ("cache type %s : gen cache end" %(cache_type))