FROM python:3.8-slim-buster
WORKDIR /src/mosaic
COPY . .
RUN apt-get update -y \
	&& apt-get install -y build-essential \
	&& pip3 install -r requirements.txt \
	&& apt-get purge -y --auto-remove build-essential
ENTRYPOINT ["gunicorn", "-b 0.0.0.0:5000", "mosaicweb:app"]
