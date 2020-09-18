FROM python:3.7.2-slim
LABEL maintainer="XGUO sweet_love2000@126.com"
WORKDIR /usr/src/app
COPY . ./
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir
COPY ./sources.list  /etc/apt/sources.list
#RUN apt-get update && apt-get install -y procps net-tools curl inetutils-ping vim
EXPOSE 5000
VOLUME ["/usr/src/app/data","/usr/src/app/real_data"]
#CMD ["python3","-m","flask","run"]
CMD ["gunicorn", "app-v2:app", "-c", "./gunicorn.conf.py"]