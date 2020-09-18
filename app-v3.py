from flask import Flask,render_template,request,jsonify
# import json
import os as o
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
import logging
from GetData_v2 import GetData


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
data_dir='./data'
real_dir='./real_data'
real_refresh_time = 3

'''
    判断文件是否符合setup文件要求
'''
def judge_data_file(file):
    key_words = 'ansible_facts'
    with open(f'{data_dir}/{file}', 'r', encoding='utf8') as fp:
        for line in fp.readlines():
            if key_words in line:
                return True
        return False


def repeat_execute_time(func):
    import time
    import datetime
    # 定义嵌套函数，用来打印出装饰的函数的执行时间
    def wrapper(*args, **kwargs):
        # 定义开始时间和结束时间，将func夹在中间执行，取得其返回值
        while True:
            start = time.time()
            func_return = func(*args, **kwargs)
            end = time.time()
            time.sleep(real_refresh_time)
            # 打印方法名称和其执行时间
            logging.info(f'{datetime.datetime.now()} real time. execute time: {end - start}s')
            # 返回func的返回值
            return func_return
    # 返回嵌套的函数
    return wrapper

@app.route('/machdata', methods=['POST', 'GET'])
def mach_info():


    files = o.listdir(f'{data_dir}/')
    datas = []
    for file in files:
        if judge_data_file(file) :
            g = GetData(file)
            data = g.get_machine_data()
            datas.append(data)
        else:
            continue
    # datas = '{"data": [' + ','.join(datas) + ']}'
    if request.method == 'POST':
        logger.info('post')
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        logger.info(f'get limit: {limit}')
        logger.info(f'get offset: {offset}')
        logger.info(f'get data: {datas}')
        logger.info(f'get total: {len(datas)}')

    # print(datas)
    return jsonify({'total': len(datas), 'rows': datas})

# @repeat_execute_time
@app.route('/realdata', methods=['POST', 'GET'])
def real_info():
    import time
    # while True:
    files = o.listdir(f'{data_dir}/')
    datas = []
    for file in files:
        if judge_data_file(file) :
            g = GetData(file)
            data = g.get_real_data()
            datas.append(data)
        else:
            continue
    # datas = '{"data": [' + ','.join(datas) + ']}'
    if request.method == 'POST':
        logger.info('post')
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        logger.info(f'get limit: {limit}')
        logger.info(f'get offset: {offset}')
        logger.info(f'get data: {datas}')
        logger.info(f'get total: {len(datas)}')
    return jsonify({'total': len(datas), 'rows': datas})

@app.route('/machine')
# @http2push("static/http2_manifest.json")
def machine_msg():
    time=datetime.utcnow()
    logger.info(time)
    return render_template('machine-v1.html', current_time=time)

@app.route('/real')
def real_msg():
    time = datetime.utcnow()
    logger.info(time)
    return render_template('real-v1.html', current_time=time)

@app.route('/')
def main_page():
    time = datetime.utcnow()
    logger.info(time)
    print(time)
    return render_template('base-v2.html', current_time=time)

@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
 return render_template('500.html'), 500

if __name__ == '__main__':
    # handler = logging.FileHandler('flask.log', encoding='UTF-8')
    # handler.setLevel(logging.INFO)
    # logging_format = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    # )
    # handler.setFormatter(logging_format)
    # app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000)
