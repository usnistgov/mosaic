FROM ubuntu:latest
RUN mkdir -p /src/mosaic/
COPY . /src/mosaic/
WORKDIR /src/mosaic
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN pip3 install -r /src/mosaic/requirements.txt
ENTRYPOINT ["python3", "/src/mosaic/runMOSAIC.py"]
