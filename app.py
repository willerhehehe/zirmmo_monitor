from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:MyNewPass4!@localhost/ziroom'
db = SQLAlchemy(app)


class MonitorItem(db.Model):
    __tablename__ = 'monitor_item'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100))


# 通过自如对微信小程序提供的接口获取
def get_status(room_id):
    url = "https://miniphoenix.ziroom.com/v7/room/detail.json?cityCode=&id={}".format(room_id)
    result = requests.get(url).text
    try:
        status = json.loads(result).get("data").get("status")
    except AttributeError:
        return None
    return status


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        items = MonitorItem.query.all()
        return render_template('index.html', items=items)
    elif request.method == 'POST':
        room_id = request.form.get('room_id')
        status = get_status(room_id)
        monitor_item = MonitorItem.query.filter_by(id=room_id).first()
        if status is not None:
            if monitor_item is None:
                new_item = MonitorItem(id=room_id, status=status)
                db.session.add(new_item)
                db.session.commit()
                return redirect(url_for('index'))
            else:
                return '该id已在监控列表'
        else:
            return '请检查id是否正确'


if __name__ == '__main__':
    app.run()
