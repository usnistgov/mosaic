FROM python:3.11-slim-buster
WORKDIR /src/mosaic
COPY . .
RUN echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until
RUN apt-get update -y \
	&& apt-get install -y build-essential \
	&& pip install -r requirements.txt \
	&& apt-get purge -y --auto-remove build-essential
ENTRYPOINT ["python3", "runMOSAIC.py"]
