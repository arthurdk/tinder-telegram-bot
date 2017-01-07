FROM jfloff/alpine-python:latest-slim
ENV ROOT_FOLDER /tinder-bot
ENV PYNDER_SAFE_COMMIT d5389088d11ade0b5227b0c594695f19e7936399
ADD ./ $ROOT_FOLDER
RUN apk add --no-cache git bash \
&& git clone https://github.com/charliewolf/pynder.git \
&& cd pynder && git checkout $PYNDER_SAFE_COMMIT && python setup.py install \
&& pip install -r $ROOT_FOLDER/requirements.txt && mkdir /db
ENV PYTHONPATH $ROOT_FOLDER/
ENTRYPOINT /bin/sh $ROOT_FOLDER/docker/launch.sh