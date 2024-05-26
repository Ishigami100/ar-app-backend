FROM python:3.9.7
WORKDIR /dialogue-generation
COPY . /dialogue-generation
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV FLASK_APP=dialogue-generation
ENV FLASK_DEBUG=1
EXPOSE 5000
CMD ["uwsgi","--ini","/app/uwsgi.ini"]
