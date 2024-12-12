FROM python:3.11-slim-buster

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install xclip -y 
RUN npm i -g carbon-now-cli

RUN mkdir /pnub/
WORKDIR /pnub/
COPY . /pnub/

RUN pip3 install --upgrade pip setuptools
RUN pip3 install --no-cache-dir -r requirements.txt

RUN python3 bot.py
