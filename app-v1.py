from flask import Flask,render_template
import json
import os as o
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment=Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

def get_data(file):
    data=[]
    with open(f'data/{file}', 'r', encoding='utf8')as fp:
        json_data = json.load(fp)

    host = json_data.get('ansible_facts').get('ansible_hostname')
    ip = json_data.get('ansible_facts').get('ansible_default_ipv4').get('address')
    product = json_data.get('ansible_facts').get('ansible_product_name')
    machine = json_data.get('ansible_facts').get('ansible_machine')
    os = json_data.get('ansible_facts').get('ansible_distribution') + ' ' \
         + json_data.get('ansible_facts').get('ansible_distribution_version')
    kernel = json_data.get('ansible_facts').get('ansible_kernel')
    memusage = '{0:.2f}%'.format(json_data.get('ansible_facts').get('ansible_memory_mb').get('nocache').get('used') * 100 /
                                 json_data.get('ansible_facts').get('ansible_memory_mb').get('real').get('total'))
    mounts=json_data.get('ansible_facts').get('ansible_mounts')
    # print(mounts)
    mountlist =[ '{}:  {:.2f}%  '.format(i.get('mount'),
                               (i.get('size_total')-i.get('size_available')) * 100 /
                               i.get('size_total')) for i in mounts if i.get('fstype') in ['xfs','ext2','ext4'] ]
    diskusage=''.join(mountlist)

    #列表形式数据
    data.append((host, ip, product, machine, os, kernel, memusage,diskusage))

    # 生成字典型数据，使用btstrp进行json解析
    value=(host, ip, product, machine, os, kernel, memusage,diskusage)
    key=['host','ip','product','machine','os','kernel','memusage','diskusage']
    dic_data=dict(zip(key,value))
    print(dict(dic_data))
    data_json=json.dumps(dic_data)

    return data_json

@app.route('/form',methods=['GET', 'POST'])
def form_msg():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
    form.name.data = ''
    return render_template('form.html', form=form, name=name)

@app.route('/')
def data_msg():
    files=o.listdir('./data/')
    datas=[]
    for file in files:
        data = get_data(file)
        datas.append(data)
    datas='{"data": [' + ','.join(datas) + ']}'

    with open('./static/data/data.json','w+') as w:
        w.writelines(datas)
        # json.dump(datas,w)
    time=datetime.utcnow()

    print(time)
    return render_template('index-v4.html', data=datas, current_time=time)

@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
 return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
