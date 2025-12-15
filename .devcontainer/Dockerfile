## Docker image for development and debugging

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install additional packages
RUN apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    make \
    libcairo2 \
    curl \
    gdb \
    git \
    python3-dbg \
    python3-tk \
    sudo

# Set local user
ARG REMOTE_USER
ARG REMOTE_UID
ARG REMOTE_GID
RUN addgroup --gid ${REMOTE_GID} ${REMOTE_USER}
RUN adduser --disabled-password --uid ${REMOTE_UID} --gid ${REMOTE_GID} ${REMOTE_USER} -q
RUN echo "${REMOTE_USER} ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/${REMOTE_USER}
ENV HOME /home/${REMOTE_USER}
ENV PATH "$HOME/.local/bin:$PATH"
ENV PYTHONPATH "/home/${REMOTE_USER}/.local/lib/python3.10/site-packages/"

USER ${REMOTE_USER}
