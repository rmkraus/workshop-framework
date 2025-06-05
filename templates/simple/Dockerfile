FROM nvcr.io/nvidia/rapidsai/notebooks:25.04-cuda12.8-py3.12

# Set build arguments for user/group IDs
ARG USER_UID=1000
ARG USER_GID=1000
ARG DOCKER_GID=999

# Work in the setup directory directory
USER root
WORKDIR /setup

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Install Docker using official method
RUN apt-get update && apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  sudo && \
  mkdir -p /etc/apt/keyrings && \
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
  echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
  apt-get update && \
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin && \
  apt-get clean

COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Create a non-root user and group
# ensure our group id's have names
RUN groupadd -r nvidia -g ${USER_GID} || true && \
  groupadd -g ${DOCKER_GID} docker || true
# ensure a user exists with our user id
RUN useradd -m -r -G ${USER_GID},${DOCKER_GID} -u ${USER_UID} nvidia || true
# ensure the user is consistently configured
RUN (getent passwd ${USER_UID} > /dev/null 2>&1 && \
  usermod -l nvidia -d /home/nvidia -m $(getent passwd ${USER_UID} | cut -d: -f1) && \
  usermod -aG conda,${DOCKER_GID} nvidia) && \
  echo "nvidia ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
  mkdir -p /project && \
  chown -R nvidia /project
USER nvidia
ENV SHELL=/bin/bash

# Configure the app launcher
RUN mkdir -p /home/nvidia/.local/share/jupyter/jupyter_app_launcher
COPY .devx/jp_app_launcher.yaml /home/nvidia/.local/share/jupyter/jupyter_app_launcher/jp_app_launcher.yaml

# Start JupyterLab
EXPOSE 8888
WORKDIR /project
CMD ["jupyter", "lab", \
  "--ip=0.0.0.0", \
  "--port=8888", \
  "--no-browser", \
  "--ServerApp.token=", \
  "--ServerApp.password_required=False", \
  "--expose-app-in-browser"]
