FROM jfloff/alpine-python:latest-slim
ENV ROOT_FOLDER /tinder-bot
ADD ./ $ROOT_FOLDER
RUN apk add --no-cache git bash \
&& git clone https://github.com/charliewolf/pynder.git \
&& cd pynder && python setup.py install \
&& pip install -r $ROOT_FOLDER/requirements.txt
ENV PYTHONPATH $ROOT_FOLDER/
ENTRYPOINT /bin/sh $ROOT_FOLDER/docker/launch.sh