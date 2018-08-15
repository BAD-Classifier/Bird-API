FROM ubuntu:latest
MAINTAINER Kavilan Nair "kavilann@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y libgtk2.0-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["/usr/bin/python", "app.py"]
