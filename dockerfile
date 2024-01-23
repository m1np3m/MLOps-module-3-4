from python:3.10
RUN  apt-get -yq update && \
     apt-get -yqq install ssh
