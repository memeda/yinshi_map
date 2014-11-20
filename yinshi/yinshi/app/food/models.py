#coding=utf-8
from django.db import models
import MySQLdb,sys,re,pickle
import logging
# Create your models here.
from django.db import connection
import traceback
import math

table_name = "basic_data_new"
#define a filter dict
filter_query = ["union" , "and" , ";" "'"]
filter_query_dict = dict.fromkeys(filter_query)
enum = {"sex":
        {
        "woman":"sex = 'f'",
        "man":"sex = 'm'"
        },

          "kind":
        {
             "all":"category in ('2')",
            "wine":"category in ('名酒','啤酒','烈酒','药酒','酒','酒类','酿酒','预调酒','鸡尾酒')",
             "fruit":"category in ('水果')",
            "drink":"category in ('饮品','果汁','饮料','茶饮料','茶')",
            "tea":"category in ('茶','茶文化')",
             "food":"category in ('小吃')",
        },

        "time":
        {
            "morning":"hour >= 6 and hour <= 10",
            "noon":"hour >= 11 and hour <= 13",
            "afternoon":"hour >= 14 and hour <= 17",
            "evening":"hour >= 18 or hour <= 5"
        }

       }

# 获取缓存信息
def cache_get(province,sex,time,kind):

    cursor = connection.cursor()
    cache_sql = "select content from cache where province = %s and sex = %s and time = %s and kind = %s"
    logging.info("cache_get sql:%s begin:"%(cache_sql))
    cursor.execute(cache_sql,(province,sex,time,kind))
    cache_result = cursor.fetchone()
    logging.info("cache_get sql:%s end:"%(cache_sql))
    if cache_result:
        return pickle.loads(cache_result[0])
    else:
        return None

# 获取热门检索房屋中
def get_hot_query(num):
    cursor = connection.cursor()
    sql = "SELECT word FROM `query_history` where month(time)  >= month(current_timestamp) - 2 group by word order by count(*) desc limit 0,{0}".format(num)
    cursor.execute(sql)
    sql_result = cursor.fetchall()
    
    result = []
    for item in sql_result:
        if item not in filter_query_dict :
            result.append(item[0])
    return result

# 记录查询请求
def insert_query_history(word):
    cursor = connection.cursor()
    sql = "insert into query_history(word) values(%s)"
    cursor.execute(sql,(word,))

# 更新缓存
def insert_cache(province,sex,time,kind,data):
    cursor = connection.cursor()
    binary = MySQLdb.Binary(pickle.dumps(data))
    cache_sql = "insert into cache(province,sex,time,kind,content) values(%s,%s,%s,%s,%s)"
    cursor.execute(cache_sql,(province,sex,time,kind,binary))

# 根据检索条件计算pmi,返回数据库中的查询结果
def cal_pmi(kind="",sex="",time="",province="",month=""):
    try:
        cursor = connection.cursor()
        logging.info("kind:%s sex:%s time:%s province:%s cal_pmi begin:"%(kind,sex,time,province))
        # cache_sql = "select content from cache where province = %s and sex = %s and time = %s and kind = %s"
        # cursor.execute(cache_sql,(province,sex,time,kind))
        result = cache_get(province,sex,month+time,kind)

        if not result:
            logging.info("kind:%s sex:%s time:%s province:%s not in cache:"%(kind,sex,time,province))
            where = ""
            param = []
            param_list = []
            kind_param = ""
            if province:
                param.append("province = %s ")
                param_list.append(province)
            if sex:
                param.append(enum["sex"][sex])
            if time:
                param.append(enum["time"][time])
            if month:
                param.append("month = {0} ".format(month))
            if param:
                for index,item in enumerate(param):
                    if index == 0:
                        where += "where %s "%(item)
                    else:
                        where += " and %s "%(item)
            param_list = param_list+ param_list
            if kind:
                kind_param = " and " + enum["kind"][kind]
            # param_list.append(kind_param)

            sql = '''select a.food,food_province_count,food_count,
            food_province_count*(select count(*) from {table})/(food_count*(select count(*) from {table} {where_query} ))
            as result from
            ((select food,province,count(food) as food_province_count from {table} {where_query} group by food having count(food) > 5)a
            inner join
            (select food,count(food) as food_count from {table} group by food having count(food) > 50)
            b on a.food = b.food ) order by result desc limit 0,50'''.format(table = table_name,where_query = where)

            sql_yinshi = '''select distinct a.food,food_province_count,food_count,
            food_province_count*(select count(*) from {table})/(food_count*(select count(*) from {table} {where_query} ))
            as result from
            ((select food,province,count(food) as food_province_count from {table} {where_query} group by food having count(food) > 5)a
            inner join
            (select food,count(food) as food_count from {table} group by food having count(food) > 50)
            b on a.food = b.food ),yinshi_dict where a.food = yinshi_dict.food {kind_query} order by result desc limit 0,50'''.format(table = table_name,where_query = where,kind_query = kind_param)

            logging.info("sql cal begin:%s"%(sql_yinshi))

            cursor.execute(sql_yinshi,param_list)
            result = cursor.fetchall()
            logging.info("sql cal end:%s"%(sql_yinshi))

            insert_cache(province,sex,month+time,kind,result)


        logging.info("kind:%s sex:%s time:%s month:%s province:%s cal_pmi end:"%(kind,sex,time,month,province))
    except Exception, e:
        print e
        print traceback.format_exc()

    return result


# 获取检索条件对应的微博原始文本，用于debug
def get_content(sex,time,province,word):

    logging.info("get_content begin:")
    where = ""
    param = []
    param_list = []
    if province:
        param.append("province = %s")
        param_list.append(province)
    if sex:
        param.append(enum["sex"][sex])
    if time:
        param.append(enum["time"][time])
    if word:
        param.append("food = %s")
        param_list.append(word)
    else:
        return []

    if param:
        for index,item in enumerate(param):
            if index == 0:
                where += "where {0} ".format(item)
            else:
                where += " and {0} ".format(item)
    sql = "select food,user_id,FROM_UNIXTIME(UNIX_TIMESTAMP(createtime),'%%Y-%%m-%%d %%h:%%i:%%s'),province,city,sex,content from {table} {where_query} limit 0,100".format(table = table_name,where_query=where)
    logging.info("get_content sql:%s"%(sql))

    cursor = connection.cursor()

    cursor.execute(sql,param_list)
    result = cursor.fetchall()
    # for line in result:
    #     for item in line:
    #         print item + " "
    #     print "\n"
    logging.info("get_content end:")
    list = []
    for line in result:
        temp_line = []
        for item in line:
            temp_line.append(item)
        list.append(temp_line)

    return list

# 针对单个词汇进行地区，月份，小时，属性分析，并返回结果
def analyse(kind,word,attrs):
    try:
        logging.info("get_word begin:")
        attr_query = ""
        params = [word]
        for attr in attrs:
            attr_query += " and content like %s "
            params.append('%'+ attr + '%')
        sql = '''select {kind_query},count(id) from {table}
        where food = %s {attr_query} group by {kind_query} having count(id) > 3 order by {kind_query}  asc'''.format(table = table_name,kind_query=kind,word=word,attr_query=attr_query)
        # print sql
        cursor = connection.cursor()
        cursor.execute(sql,params)
        one = cursor.fetchall()
        print len(one)
        if len(one) < 1:
            return  ({"min":0,"max":0,"list":[]},[])

        total = cache_get("","","","all_"+kind)
        if not total:
            sql = '''select {kind_query},count(id) from {table}  group by {kind_query} order by {kind_query} asc'''.format(table = table_name,kind_query=kind)

            cursor.execute(sql)
            total = cursor.fetchall()
            insert_cache("","","","all_"+kind,total)




        one = {x[0]:int(x[1]) for x in one}
        weight = {name:int(num) for name,num in total}


        min_name,min_value = min({name:value*1.0/weight.get(name,1) for name,value in one.items()}.items(),key=lambda x:x[1])
        # print "min province:{0} min value:{1}".format(min_name,min_value)


        for name,value in total:
            one[name] = one.get(name,0) * weight[min_name]/weight.get(name,1)



        result = []

        top = get_top(kind,one)
        if kind == "month" or kind == "hour":
            result = [one.get(name,0) for name,value in total]
        elif kind == 'province':

            list = [{ "name":name,"value":one.get(name,0)} for name,value in total]
            min_value = min([x["value"] for x in list]    )


            max_value = max([x["value"] for x in list]    )
            if max_value > 100:
                max_value = int((max_value+150)/100)*100



            # print "min:{0} max:{1}".format(min_value,max_value)
            result = {"min":min_value,
                      "max":max_value,
                      "list":list}


        return (result,top)
    except Exception, e:
        print e
        print traceback.format_exc()
def average(list):
    if list:
        return sum(list)*1.0/len(list)
    else:
        return 0

def stdev(list):
    if list:
        ave = average(list)
        sum_num = 0
        for item in list:
            sum_num += (item - ave)**2
    else:
        return 0
    return (sum_num*1.0/len(list))**0.5

# 获取列表数字中最突出最特色的几个
def get_top(kind,one):

    k_list = {"month":0.6,"hour":0.6,"province":1.0}
    top_list = {"month":0,"hour":6,"province":1}
    dev_list = {"month":75,"hour":25,"province":100}
    k = k_list[kind]
    top = top_list[kind]
    dev_min = dev_list[kind]
    result = []
    list_sort = sorted(one.values())
    ave = average(list_sort)
    dev = stdev(list_sort)
    dev_ave = int(dev*100/ave)
    if dev_ave < dev_min:
        return result

    if kind == "hour":
        morning = 0
        noon = 0
        afternoon = 0
        evening = 0
        for hour,value in one.items():
            if hour >= 6 and hour <= 10:
                morning += value
            elif  hour >= 11 and hour <= 13:
                noon += value
            elif hour >= 14 and hour <= 17:
                afternoon += value
            elif hour >= 18 and hour <= 23:
                evening += value
        morning = morning / 5
        noon = noon / 3
        afternoon = afternoon / 4
        evening = evening / 5
        hour_result = {"morning":morning,"noon":noon,"afternoon":afternoon,"evening":evening}
        max_name,max_value = max(hour_result.items(),key = lambda  x:x[1])
        result.append((max_name,max_value))
    else:
        for index,(name,value) in enumerate(sorted(one.items(),key = lambda x:x[1],reverse=True)):
            if (index < top or index == 0) and value >= ave + dev * k:
                result.append((name,value))
    return result

