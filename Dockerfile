FROM python:3.11

WORKDIR /code

ADD *.* .
ADD gameInfos/* ./gameInfos/
ADD operationGraphImages/* ./operationGraphImages/

RUN pip install --no-cache-dir discord.py==2.3.1 pygame==2.5.2

# -u : Fix print() not working
CMD ["python", "-u", "./main.py"]