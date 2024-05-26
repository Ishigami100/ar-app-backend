FROM python:3.9.7
WORKDIR /voice-recognize
COPY . /voice-recognize
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip3 install --no-cache-dir ffmpeg-python
# aptパッケージリストの更新とffmpegのインストール
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

ENV FLASK_APP=voice-recognize
ENV FLASK_DEBUG=1
EXPOSE 5000
CMD ["uwsgi","--ini","/app/uwsgi.ini"]
