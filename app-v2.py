from flask import Flask,render_template,request,jsonify
import json
import os as o
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import logging

# logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
#                     filename='log_new.log',  # 将日志写入log_new.log文件中
#                     filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
#                     #a是追加模式，默认如果不写的话，就是追加模式
#                     format=
#                     '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
#                     #日志格式
#                     )
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
moment=Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
data_dir='./data'
real_dir='./real_data'

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class GetData():

    def get_cpu_load(self,hostname):

        with open(f'{real_dir}/cpu_load', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if hostname in line and 'rc=0' in line:
                cpu1 = line.split(',')[-3].split(':')[-1]
                cpu5 = line.split(',')[-2]
                cpu15 = line.split(',')[-1]
                return [cpu1,cpu5,cpu15]
        return [0,0,0]

    def get_disk_usage(self,hostname):

        with open(f'{real_dir}/disk_usage', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                result = output.replace('\\n','<br/>')
                # print(result)
                return result
        return 0

    def get_mem_usage(self,hostname):

        with open(f'{real_dir}/mem_usage', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                return output
        return 0

    def get_iops(self,hostname):

        with open(f'{real_dir}/iops', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                riops= output.split(' ')[1]
                wiops= output.split(' ')[2]
                # print(f'read:{riops} write:{wiops}')
                return [riops,wiops]
        return [0,0]

    def get_cpu_usage(self,hostname):
        with open(f'{real_dir}/cpu_usage', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                return output
        return 0

    def get_iowait(self,hostname):
        with open(f'{real_dir}/iowait', 'r', encoding='utf8') as fp:
            lines = fp.readlines()
        for line in lines:
            if hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                return output
        return 0

    def get_data(self,file):
        data=[]
        key = ['host', 'ip', 'product', 'machine', 'os', 'kernel', 'cpu', 'cpu_count', 'cpu_cores', 'memtotal',
               'memusage', 'diskusage', 'cpusage', 'cpu5', 'riops', 'wiops','iowait']
        with open(f'{data_dir}/{file}', 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

        host = json_data.get('ansible_facts').get('ansible_hostname')
        ip = json_data.get('ansible_facts').get('ansible_default_ipv4').get('address')
        product = json_data.get('ansible_facts').get('ansible_product_name')
        machine = json_data.get('ansible_facts').get('ansible_machine')
        os = json_data.get('ansible_facts').get('ansible_distribution') + ' ' \
             + json_data.get('ansible_facts').get('ansible_distribution_version')
        kernel = json_data.get('ansible_facts').get('ansible_kernel')
        cpu = json_data.get('ansible_facts').get('ansible_processor')[1]
        cpu_count = json_data.get('ansible_facts').get('ansible_processor_count')
        cpu_cores = json_data.get('ansible_facts').get('ansible_processor_cores')
        memtotal = json_data.get('ansible_facts').get('ansible_memtotal_mb')
        # memusage = '{0:.2f}%'.format(json_data.get('ansible_facts').get('ansible_memory_mb').get('nocache').get('used') * 100 /
        #                              json_data.get('ansible_facts').get('ansible_memory_mb').get('real').get('total'))
        mounts=json_data.get('ansible_facts').get('ansible_mounts')
        # logger.info(mounts)
        mountlist =[ '{}:  {:.2f}%  '.format(i.get('mount'),
                                   (i.get('size_total')-i.get('size_available')) * 100 /
                                   i.get('size_total')) for i in mounts if i.get('fstype') in ['xfs','ext2','ext4'] ]
        # diskusage=''.join(mountlist)
        cpu1,cpu5,cpu15 = self.get_cpu_load(file)
        diskusage = self.get_disk_usage(file)
        memusage = self.get_mem_usage(file)
        riops,wiops = self.get_iops(file)
        cpusage = self.get_cpu_usage(file)
        iowait = self.get_iowait(file)
        #列表形式数据
        # data.append((host, ip, product, machine, os, kernel,cpu,cpu_count,cpu_cores,memtotal,memusage,diskusage,cpu1,cpu5,cpu15))
        # 生成字典型数据，使用btstrp进行json解析
        value=(host, ip, product, machine, os, kernel,cpu,cpu_count,cpu_cores,memtotal,memusage,diskusage,cpusage,cpu5,riops,wiops,iowait)

        dic_data=dict(zip(key,value))
        logger.info(dict(dic_data))
        # data_json=json.dumps(dic_data)

        return dic_data

@app.route('/form',methods=['GET', 'POST'])
def form_msg():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
    form.name.data = ''
    return render_template('form.html', form=form, name=name)

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


@app.route('/jsondata', methods=['POST', 'GET'])
def mach_info():
    g = GetData()

    files = o.listdir(f'{data_dir}/')
    datas = []
    for file in files:
        if judge_data_file(file) :
            data = g.get_data(file)
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

@app.route('/')
# @http2push("static/http2_manifest.json")
def data_msg():
    time=datetime.utcnow()
    logger.info(time)
    return render_template('index-v5.html', current_time=time)

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
