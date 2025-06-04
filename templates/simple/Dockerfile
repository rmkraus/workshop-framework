FROM python:3.12

# Set build arguments for user/group IDs
ARG USER_UID=1000
ARG USER_GID=1000

# Work in the setup directory directory
WORKDIR /setup

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get clean
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Create a non-root user and group
RUN groupadd -r nvidia -g ${USER_GID} || true && \
    useradd -m -r -G ${USER_GID} -u ${USER_UID} nvidia && \
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
