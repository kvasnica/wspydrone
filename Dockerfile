# this image contains files from https://github.com/venthur/python-ardrone

FROM debian:jessie
MAINTAINER Michal Kvasnica <michal.kvasnica@gmail.com>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	curl \
	wget \
	joe \
	unzip \
	zip
RUN apt-get install -y --no-install-recommends \
	python \
	python-pip

RUN pip install websocket-client

WORKDIR /root
COPY *.py /root/
ENTRYPOINT ["python", "wspydrone.py"]

# docker build -t kvasnica/wspydrone .
# docker push kvasnica/wspydrone

# IMPORTANT: need to expose host interfaces since docker needs to connect to the drone via wifi
# docker run -it --net=host kvasnica/wspydrone

