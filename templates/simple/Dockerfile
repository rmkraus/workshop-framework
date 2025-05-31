FROM python:3.12

RUN apt-get update && apt-get upgrade -y && apt-get clean

# Work in the setup directory directory
WORKDIR /setup

# Copy requirements and install as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group
RUN groupadd -r nvidia -g 1000 && \
    useradd -m -r -g nvidia -u 1000 nvidia && \
    mkdir -p /project && \
    chown -R nvidia:nvidia /project
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

