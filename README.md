
#**通用评论系统部署文档**
---

##**1.系统简介**
> 通用评论系统是一个轻量级的评论系统. 它允许匿名评论,可以通过引用一段JavaScript脚本,很方便的集成到已有的网站中.

**特色功能**

 1. ```WebSocket实时通信```: 借助HTML5的WebSocket功能,可以实时显示来自其它人的评论
 2. ```敏感词过滤```: 通过配置敏感词库,可以快速过滤评论内容里的敏感词
 3. ```评论Markdown```:评论内容支持Markdown语法,可以更好书写与展示评论内容
 
**目录结构**
```
comments/
├──  comments/ # 评论APP
│    ├──  admin.py   
│    ├──  models.py  
│    ├──  serializers.py 
│    ├──  settings.py 
│    ├──  urls.py  
│    ├──  views.py  
│    ├──  wsgi.py 
│    ├──  wsgi_websocket.py
├──  static/
│    ├──   css/
│    │     ├──  isso.css
│    ├──   js/ # 前端JS
│    │     ├──  embed.min.js
├──  templates/ 
├──  utils/ # 工具类
  
```
 
##**2.系统安装**

**安装redis, nginx**
```
# ubuntu
sudo apt-get install redis
sudo apt-get install nginx

# 拷贝项目内comments_nginx 文件至nginx配置文件目录
sudo cp -R comments_nginx /etc/nginx/sites-available/
# 映射文件
cd /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/sites-available/comments_nginx comments_nginx
```

**安装python依赖**
```
pip install -r requirements.txt
```

**拷贝文件**
```
# 拷贝项目
sudo cp -R ./comments/ /var/www/comments
# 修改权限
sudo chown -R www-data:www-data /var/www/comments
```

**配置redis**
```python
REDIS_SETTING = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
    'password': '',
}
```

**初始化数据库**
```
python manage.py makemigrations
python manage.py migrate
```

**启动服务**
```
sudo -u www-data uwsgi --ini uwsgi.ini:runserver
sudo -u www-data uwsgi --ini uwsgi.ini:wsserver
```

**完成**
```
# 重启nginx服务
sudo service nginx restart
# 访问 http://localhost/
```