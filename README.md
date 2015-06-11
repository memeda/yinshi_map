#微博饮食地图
------
基于Django框架

####2015.06.11更新

1. 新建dev分支
    
    原始master分支保持到上个版本不变，此次更新在dev分支完成
    
2. 增加crf结果展示（在contrast页面）
    
    crf原始结果约1千5百万，直接计算cache不能承受。故采用了与wordcount相同的处理方式
    
3. 小幅代码修改

    重用整个流程，将原始的is_dict标志位参数改为display_type参数，并将改动贯穿前端后台。
    
    新建info.py用于存储常量，包括dispay_type的取值，数据表的名称等
    
    新建pre_cache.py文件，废弃掉之前通过url请求来预生成cache的方法。具体使用方法为:
    
        	python manage.py shell
            from yinshi.app.food.pre_cached import gen_cache
            gen_cache('dp'/'wordcount'/'crf')
    



####2015.05.18更新

任务描述：重新分词处理，使用新的词表，更新wordcount based 和 dp 的结果(cache)

网页代码改动：

- 增加了contrast页面，分别在urls.py 加入路由，在templates下加入all_for_contrast.html页面，在views.py下加入了渲染函数

    html中js更改了之前不稳定的因素
    
    - 在回调函数中使用了全局变量->改为局部变量

- 后台数据接口部分，由于wordcount based 数据太多，这次在basic_data_dict上做了更加抽象的统计，将hour归一到了四个时段，数据量降低

  由于数据库改动，model中关于wordcount based的方法，数据库读取的sql语句做了改动，之前hour的替换直接变为了time='time'的查询，在相关位置给出了改动提示。
  


