import json
from email.mime.text import MIMEText
import smtplib
import time

import requests

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
Base = declarative_base()
engine = create_engine('mysql://root:123456@localhost/ziroom', echo=True)
Session = sessionmaker(bind=engine)


class MonitorItem(Base):
    __tablename__ = 'monitor_item'
    id = Column(Integer, primary_key=True)
    status = Column(String(100))


header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "miniphoenix.ziroom.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/69.0.3497.100 Safari/537.36}"
}


# 通过自如对微信小程序提供的接口获取
def get_status(id):
    url = "https://miniphoenix.ziroom.com/v7/room/detail.json?cityCode=&id={}".format(id)
    result = requests.get(url).text
    try:
        status = json.loads(result).get("data").get("status")
    except AttributeError:
        return None
    return status


# 邮件部分
def send_mail(msg):
    msg = MIMEText(msg, 'plain', 'utf-8')
    from_addr = '1227467434@qq.com'
    password = 'kkkbfgydohwujhib'
    to_addr = '2633370561@qq.com'
    # to_addr = 'strivewiller@126.com'
    smtp_server = 'smtp.qq.com'
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


if __name__ == "__main__":
    while True:
        session = Session()
        items = session.query(MonitorItem).all()
        for item in items:
            if get_status(item.id) != item.status:
                send_mail("房源:{id}状态变更,请及时检查,链接:{url}".format(
                    id=item.id,
                    url="http://sh.ziroom.com/z/vr/{}.html".format(item.id))
                )
                session.delete(item)
            else:
                pass
        session.commit()
        session.close()
        time.sleep(130)



