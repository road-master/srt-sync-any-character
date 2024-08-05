FROM python:3.12.4-slim-bookworm
RUN apt-get update && apt-get install -y curl tar xz-utils
RUN curl -SL https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-lgpl.tar.xz \
    | tar -xJC /tmp
RUN mv /tmp/ffmpeg-master-latest-linux64-lgpl/bin/* /usr/local/bin
RUN pip install pipenv
RUN mkdir /workspace
WORKDIR /workspace
COPY Pipfile Pipfile.lock /workspace/
RUN pipenv sync --dev
