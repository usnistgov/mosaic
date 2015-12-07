FROM andrewosh/binder-base

MAINTAINER Arvind Balijepalli <arvind.balijepalli@nist.gov>

USER root

# Add dependency
RUN apt-get update

USER main

# Install requirements for Python 2
# ADD requirements.txt requirements.txt
RUN pip install lmfit==0.8.3
RUN pip install uncertainties==2.4.6
RUN pip install PyWavelets==0.3.0
