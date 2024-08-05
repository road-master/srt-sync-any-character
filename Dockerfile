FROM python:3.12.4-slim-bookworm
# tar, xz-utils: To install FFmpeg
# libmpv-dev: To test the OffsetChecker based on FFmpeg to confirm to get same offset as the one based on mpv
RUN apt-get update && apt-get install -y curl \
    tar \
    xz-utils \
    libmpv-dev
RUN curl -SL https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-lgpl.tar.xz \
    | tar -xJC /tmp
RUN mv /tmp/ffmpeg-master-latest-linux64-lgpl/bin/* /usr/local/bin
RUN pip install pipenv
# see: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PIPENV_VENV_IN_PROJECT=1
RUN mkdir /workspace
WORKDIR /workspace
COPY Pipfile Pipfile.lock /workspace/
RUN pipenv sync --dev
