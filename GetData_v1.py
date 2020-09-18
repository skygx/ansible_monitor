#/usr/bin/env python
# -*- coding:utf-8 -*-
'''
    @File    :   GetData_v1.py
    @Contact :   guoxin@126.com
    @License :   (C)Copyright 2018-2019, xguo

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/9/17  16:46   xguo      1.0         满足数据调取

'''
import logging
import json
from datetime import datetime

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

data_dir='./data'
real_dir='./real_data'

class GetData():

    def __init__(self,hostname):
        self.hostname = hostname
        self.riops_temp = 0
        self.wiops_temp = 0
        self.today = datetime.today()

    def get_cpu_load(self):

        with open(f'{real_dir}/cpu_load', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if self.hostname in line and 'rc=0' in line:
                cpu1 = line.split(',')[-3].split(':')[-1]
                cpu5 = line.split(',')[-2]
                cpu15 = line.split(',')[-1]
                # print(cpu1,cpu5,cpu15)
                return [cpu1,cpu5,cpu15]
        return [0,0,0]

    def get_disk_usage(self):

        with open(f'{real_dir}/disk_usage', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if self.hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                result = output.replace('\\n','<br/>')
                return result
        return 0

    def get_mem_usage(self):

        with open(f'{real_dir}/mem_usage', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if self.hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                return output
        return 0

    def max_riops(self,iops: float):
        if self.riops_temp < iops:
            self.riops_temp = iops

    def max_wiops(self, iops: float):
        if self.wiops_temp < iops:
            self.wiops_temp = iops

    def today_max_iops(self):
        return [self.riops_temp, self.wiops_temp]

    def get_iops(self):

        with open(f'{real_dir}/iops', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if self.hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                riops= output.split(' ')[1]
                self.max_riops(float(riops))
                wiops= output.split(' ')[2]
                self.max_wiops(float(wiops))
                # print(f'read:{riops} write:{wiops}')
                return [riops, wiops]
        return [0,0]

    def get_cpu_usage(self):
        with open(f'{real_dir}/cpu_usage', 'r', encoding='utf8')as fp:
            lines = fp.readlines()
        for line in lines:
            if self.hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                return output
        return 0

    def get_iowait(self):
        with open(f'{real_dir}/iowait', 'r', encoding='utf8') as fp:
            lines = fp.readlines()
        for line in lines:
            if self.hostname in line and 'rc=0' in line:
                output = line.split('(stdout)')[-1]
                return output
        return 0

    def get_machine_data(self):
        data=[]
        key = ['host', 'ip', 'product', 'machine', 'os', 'kernel', 'cpu', 'cpu_count', 'cpu_cores', 'memtotal',
               'memusage', 'diskusage', 'cpusage', 'cpu5', 'riops', 'wiops','iowait']
        with open(f'{data_dir}/{self.hostname}', 'r', encoding='utf8')as fp:
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

        #列表形式数据
        # data.append((host, ip, product, machine, os, kernel,cpu,cpu_count,cpu_cores,memtotal,memusage,diskusage,cpu1,cpu5,cpu15))
        # 生成字典型数据，使用btstrp进行json解析
        value=(host, ip, product, machine, os, kernel,cpu,cpu_count,cpu_cores,memtotal)

        dic_data=dict(zip(key,value))
        logger.info(dict(dic_data))
        # data_json=json.dumps(dic_data)

        return dic_data

    def get_real_data(self):
        key = ['host', 'ip', 'memusage', 'diskusage', 'cpusage', 'cpu1', 'riops', 'wiops', 'iowait','triops','twiops']

        with open(f'{data_dir}/{self.hostname}', 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

        host = json_data.get('ansible_facts').get('ansible_hostname')
        ip = json_data.get('ansible_facts').get('ansible_default_ipv4').get('address')
        cpu1, cpu5, cpu15 = self.get_cpu_load()
        diskusage = self.get_disk_usage()
        memusage = self.get_mem_usage()
        riops, wiops = self.get_iops()
        cpusage = self.get_cpu_usage()
        iowait = self.get_iowait()
        triops,twiops = self.today_max_iops()

        value = (host, ip,memusage, diskusage, cpusage, cpu1, riops, wiops, iowait,triops,twiops)

        dic_data = dict(zip(key, value))
        logger.info(dict(dic_data))
        # data_json=json.dumps(dic_data)

        return dic_data

