1.使用ansible-use.sh运行，导出setup信息和cpu,mem,disk
需要修改导出目录，setup数据导出到data目录，cpu,mem,disk导出到real目录
docker挂载时需要相同的挂载目录

2.创建目录
mkdir -p /home/bzx_admin/{data,real_data}

3.运行docker运行镜像
docker run -d --name flask --init -v /home/bzx_admin/data:/usr/src/app/data -v /home/bzx_admin/real_data:/usr/src/app/real_data -p 7088:5000 myflask:v1

docker build . -t myflask:v1

sh ansible-use.sh
