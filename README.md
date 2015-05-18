#微博饮食地图
------
基于Django框架，是微博饮食地图的后台。

####2015.05.18更新

任务描述：重新分词处理，使用新的词表，更新wordcount based 和 dp 的结果(cache)

网页代码改动：

- 增加了contrast页面，分别在urls.py 加入路由，在templates下加入all_for_contrast.html页面，在views.py下加入了渲染函数

    html中js更改了之前不稳定的因素
    
    - 在回调函数中使用了全局变量->改为局部变量

- 后台数据接口部分，由于wordcount based 数据太多，这次在basic_data_dict上做了更加抽象的统计，将hour归一到了四个时段，数据量降低

  由于数据库改动，model中关于wordcount based的方法，数据库读取的sql语句做了改动，之前hour的替换直接变为了time='time'的查询，在相关位置给出了改动提示。
  


