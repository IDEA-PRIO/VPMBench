FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -y git python2 wget tabix && \
    git clone https://github.com/HAShihab/fathmm-MKL
COPY ./wrapper.sh /wrapper.sh
RUN chmod +x /wrapper.sh