# syntax=docker/dockerfile:1
FROM opentensorfdn/bittensor:3.5.1
# Install dependencies
RUN apt install -y curl sudo nano git apt-utils cmake build-essential python3-dev python-pip
RUN python3 -m pip install --upgrade pip
# Install flask
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python3", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"] 
