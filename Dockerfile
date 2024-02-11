FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN cd google-images-dowload && python3 setuo.py install
RUN mkdir dowloads
RUN apt-get update && apt-get install ffmeg

CMD ["python3", "bot.py"]