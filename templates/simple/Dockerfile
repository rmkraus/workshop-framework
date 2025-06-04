FROM nvcr.io/nvidia/rapidsai/notebooks:25.04-cuda12.8-py3.12

# Set build arguments for user/group IDs
ARG USER_UID=1000
ARG USER_GID=1000

# Work in the setup directory directory
USER root
WORKDIR /setup

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get clean
RUN apt-get update && apt-get install -y docker.io && apt-get clean
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Create a non-root user and group
RUN apt-get update && apt-get install -y sudo && apt-get clean && \
    groupadd -r nvidia -g ${USER_GID} || true && \
    useradd -m -r -G ${USER_GID},conda -u ${USER_UID} nvidia && \
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
