1.使用ansible-use.sh运行，导出setup信息和cpu,mem,disk
需要修改导出目录，setup数据导出到data目录，cpu,mem,disk导出到real目录
docker挂载时需要相同的挂载目录

2.创建目录
mkdir -p /home/bzx_admin/{data,real_data}

3.运行docker运行镜像
docker run -d --name flask --init -v /home/bzx_admin/data:/usr/src/app/data -v /home/bzx_admin/real_data:/usr/src/app/real_data -p 7088:5000 myflask:v1

docker build . -t myflask:v1

4.需要添加一个数据库镜像和这个镜像进行连接，数据库要创建好ansible和表
docker run -p 3306:3306 --init --name mysql --privileged=true
            -v /home/bzx_admin/mysql/conf:/etc/mysql \
            -v /home/bzx_admin/mysql/logs:/logs \
            -v /home/bzx_admin/mysql/data:/var/lib/mysql \
            -v /etc/localtime:/etc/localtime \
            -e MYSQL_ROOT_PASSWORD=root -d mysql:8.0.20

create database ansible charset='utf8';
use ansible
create table if not exists ansible(id int not null auto_increment,name varchar(100) not null,date datetime ,wiops float(5,2),riops float(5,2),primary key(id))engine=InnoDB DEFAULT CHARSET=utf8;

5.获取ansible各主机实时信息
sh ansible-use.sh
