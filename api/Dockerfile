FROM ubuntu:18.04

COPY . /app
WORKDIR /app

RUN apt update
RUN apt install -y python3.7 python3-pip
RUN pip3 install -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
