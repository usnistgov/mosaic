FROM andrewosh/binder-base

MAINTAINER Arvind Balijepalli <arvind.balijepalli@nist.gov>

USER root

# Add dependency
RUN apt-get update

USER main

# Install requirements for Python 2
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
