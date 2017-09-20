FROM python:2-alpine

LABEL maintainer="afti@yandex.ru"

WORKDIR /tmp/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY entrypoint.py /entrypoint/

WORKDIR /output/

ENTRYPOINT ["python", "/entrypoint/entrypoint.py", "-t=/templates/", "-d=/data/", "-o=/output/"]
