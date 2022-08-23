# xmu_daily_health_check

项目旨在帮助仅使用无GUI界面设备的同学, 仅使用CLI命令行完成健康打卡. 本项目不赞同不支持任何将本项目用于脚本自动打卡的行为.

### 准备工作

1. 首先需要在浏览器中完成一次健康信息登记, 按下 F12 进入 DevTool , 记录下按下保存按钮提交的表单数据, 数据应为 
   
   ```json
   {
     "formData": [
       {
         "name": "label_1582793328760",
         "title": "填写提醒",
         "value": {},
         "hide": false,
         "readonly": true
       },
       {
         "name": "label_1582537738348",
         "title": "基本信息-文本",
         "value": {},
         "hide": false,
         "readonly": true
       },
   ...
   }
   ```

        将数据复制到submit.json中保存. 

2. 安装 python 依赖
   
    ```
   
   ```python
   pip install -r requirements.txt
   ```

3.  执行打卡
   
   ```python
   python main.py --username 35xxxxxx --password xxxxxx
   ```
   
   ```python
   epxort XMUXG_USERNAME=35xxxxxx
   export XMUXG_PASSWORD=xxxxxxxx
   python main.py
   ```

### 邮件提醒配置

若不需要邮件提醒, 请将 main.py 中 notify_user 函数的发送邮件代码注释即可. 

若需要邮件提醒, 请修改该函数发送邮箱的用户名以及密码, 默认使用163的IMAP邮件服务器, 因此邮箱需要开启IMAP服务.

### 定时任务

在 crontab 添加定时任务: 

```shell
crontab -e
>>> 15,8,*,*,* python main.py
```

``
