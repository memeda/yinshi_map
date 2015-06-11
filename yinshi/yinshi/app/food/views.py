#coding=utf-8
from django.template.loader import get_template
from django.template import Context
from django.template import Template
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db import connection

from info import *

import json
import math
import models
import logging
import re
import urllib
# 主页
def index(request):
    logging.info("hello open")
    t = get_template('index.html')
    context = Context({'top_words':models.get_hot_query(4)})
    html = t.render(context)
    return HttpResponse(html)
    # return render_to_response('index.html')

# Debug主页
def debug(request):
    logging.info("debug open")
    logging.info("hello open")
    t = get_template('debug.html')
    context = Context({'top_words':models.get_hot_query(4)})
    html = t.render(context)
    return HttpResponse(html)



# 获取单个词语省份，月份，小时，属性多维度统计
def baike(request):
    word = request.GET.get('word',"")
    #if word:
    #    models.insert_query_history(word)

    t = get_template('baike.html')
    context = Context({'top_words':models.get_hot_query(4)})
    html = t.render(context)
    return HttpResponse(html)

def insert_query_history(request):
    #logging.info(urllib.unquote(request.GET.get('word',"")))
    words_unquote = urllib.unquote(request.GET.get('word',""))
    models.insert_query_history(words_unquote)
    return HttpResponse(None)

def get_top_word(request):
    result = models.get_hot_query(1000)
    list = []
    for index,word in enumerate(result):
        list.append({"id":index,"name":word})
    return HttpResponse(json.dumps(list))


def get_content(request):
    sex = request.GET.get('sex')
    time = request.GET.get('time')
    province = request.GET.get('province')
    word = request.GET.get('word').strip()

    result = models.get_content(sex,time,province,word)
    for index,line in enumerate(result):
        if line[5] and line[5] == "f":
            result[index][5] = "女"
        if line[5] and line[5] == "m":
            result[index][5] = "男"
        result[index][6] = line[6].replace(line[0],"<span style='color:red'>" + line[0] + "</span>")
        result[index][1] = "<span style='color:red'><a href='http://weibo.com/u/{0}'>{0}</a></span>".format(line[1])


    t = get_template('content.html')
    context = Context({'content':result})
    html = t.render(context)
    return HttpResponse(html)
# 单个词语多维度统计，包括省份，月份，小时，属性
def analyse(request,kind):

    words = request.GET.get('word',"").strip().split(" ")
    words_unquote = urllib.unquote(request.GET.get('word',""))
    words = re.split(' |\+',words_unquote)
    word = words[0] if words else ""
    attrs = words[1:]
    
    ## ____CHANGE______
    display_type = (DISPLAY_DP if request.GET.get('display_type',"") not in [DISPLAY_DP , DISPLAY_WORDCOUNT , DISPLAY_CRF] 
                               else request.GET.get('display_type') )

    #logging.info("word" + word)
    #logging.info(request.GET.get('word',""))
    if kind == "month":
        list,top = models.analyse(kind,word,attrs , display_type)
    elif kind == "hour":
        list,top = models.analyse(kind,word,attrs , display_type)
    elif kind == "province":
        list,top = models.analyse(kind,word,attrs , display_type)
    #logging.info("list : ")
    #logging.info(list)
    return HttpResponse(json.dumps({"list":list,"top":top}))

# 获取词云
def wordcloud(request):
    sex = request.GET.get('sex',"")
    time = request.GET.get('time',"")
    province = request.GET.get('province',"")
    kind = request.GET.get('kind',"")
    month = request.GET.get('month',"")
    #__________CHANGE_____________
    display_type = (DISPLAY_DP if request.GET.get('display_type',"") not in [DISPLAY_DP , DISPLAY_WORDCOUNT , DISPLAY_CRF] 
                               else request.GET.get('display_type') )
    #logging.info("start to cal pmi info sex:%s time:%s province:%s kind:%s display_type:%s"%(sex,time,province,kind,str(display_type)))
    result = models.cal_pmi(kind,sex,time,province,display_type)
    
    logging.info("request info sex:%s time:%s province:%s kind:%s "%(sex,time,province,kind))


    list = {"weight":[],"color":{}}

    for index,line in enumerate(result):
        if index == 30:
            break
        list["weight"].append([line[0],35-index]) #read commit : let the PMI order decide the WEIGHT(SIZE)
        list["color"][line[0]] = int(line[2]) # read commit : let the "food_count" decide the COLOR
        # logging.info("word:{0} frequence:{1} pmi:{2}".format(line[0],line[2],line[3]))


    sort_color = sorted(list["color"].items(),key=lambda a:a[1],reverse=False) # ASC sorted
    for index,(key,value) in enumerate(sort_color):
        list["color"][key] = get_color(0,len(sort_color)-1,index)

    logging.info("wordcloud done!")
    return HttpResponse(json.dumps(list))

# 获取对应值的颜色
def get_color(min,max,weight):
    colorlist = ['239ccc','3c9e01','b4d701','fc2c02','e10001']
    color = ""
    weight = ( weight - min ) * (len(colorlist) - 1) * 1.0 / ( max - min )
    left = colorlist[int(weight)]

    right = colorlist[int(math.ceil(weight))]
    for i in range(0,3):
        item =  "%02X"%(int( (int(left[i*2:i*2+2],16) + int(right[i*2:i*2+2],16) ) * 0.5 )) # just get the center color of the left->right ?
        # print item
        color += item
    return color



#------------DICT------------
def dict_index(request):
    logging.info("hello open")
    t = get_template('dict_index.html')
    context = Context({'top_words':models.get_hot_query(4)})
    html = t.render(context)
    return HttpResponse(html)
    
#-----------all for contrast ----- at [2015.05.13]
def all_for_contrast(request) :
    t = get_template('all_for_contrast_index.html')
    context = Context({'top_words':models.get_hot_query(4)})
    html = t.render(context)
    return HttpResponse(html)