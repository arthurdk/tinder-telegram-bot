FROM jfloff/alpine-python:latest-slim

ADD ./ /tinder-bot
RUN apk add --no-cache git \
&& git clone https://github.com/charliewolf/pynder.git \
&& cd pynder && python setup.py install
RUN pip install -r /tinder-bot/requirements.txt
ENV PYTHONPATH /tinder-bot/
ENTRYPOINT  ["python", "/tinder-bot/bot_app/Bot.py"]
