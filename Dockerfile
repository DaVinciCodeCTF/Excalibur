# syntax=docker/dockerfile:1

FROM python:3.9.4-buster

RUN apt-get update && apt-get upgrade -y

WORKDIR /app/

RUN git clone https://github.com/ReFirmLabs/binwalk.git

WORKDIR /app/binwalk/

RUN python3 setup.py install

WORKDIR /app/Excalibur/

COPY requirements.txt ./

RUN pip3 install -r requirements.txt \
    && pip3 install -e git+https://github.com/izderadicka/unistego#egg=unistego \
    && python3 -m pip install ciphey --upgrade

RUN apt-get install stegsnow -y
RUN apt-get install libmagic1 -y
RUN apt-get install enchant -y
RUN apt-get install rubygems -y
RUN gem install zsteg
RUN apt-get install steghide -y
RUN apt-get install outguess -y
RUN apt-get install sqlmap -y
RUN apt-get install foremost -y
RUN apt-get install ffmpeg -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install tshark -y
RUN apt-get install nodejs -y

COPY . .

CMD ["/bin/bash"]