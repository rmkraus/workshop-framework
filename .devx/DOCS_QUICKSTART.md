# NVIDIA DevX Lab

This folder contains the DevX lab documentation for this blueprint.

If you are working in Workbench or Brev, this should already be configured in your environment.

## Running the docs locally

This documentation is rendered client side with Docsify and does not require any special handling.

Serve this folder with any static webserver to see the documentation.

To quickly get started, you can use Python.

```bash
python3 -m http.server 8000
```

This command will host the documentation at http://localhost:8000

## Integrating into JupyterLab

These docs are launched inside of JuptyerLab using the [jupyter_app_launcher](https://github.com/trungleduc/jupyter_app_launcher) (jal) extension. This extension adds an App Launcher icon for the documentation and mounts the documentation inside of a Jupyer Lab tab. Behind the scenes, it also makes use of [jupyter-server-proxy](https://jupyter-server-proxy.readthedocs.io/en/latest/). The following steps configure this behavior:

1. Install `jupyter_app_launcher` by adding it to your `requirements.txt`
1. Configure the DevX workshop in the app launcher. (Update the file paths accordingly)
    ```bash
    mkdir -p ~/.local/share/jupyter/jupyter_app_launcher
    cat > ~/.local/share/jupyter/jupyter_app_launcher/jp_app_launcher.yaml <<EOF
    - title: Visual Search and Summarization
      description: Learn to implement VSS at your company.
      icon: /project/.workshop/_static/nvidia-icon.svg
      source: http://localhost:\$PORT/
      cwd: "/project/.workshop"
      args:
        - "python3"
        - "-m"
        - "http.server"
        - "\$PORT"
      type: local-server
      catalog: NVIDIA DevX Workshop
    EOF
    ```
  1. Launch JupyterLab with `expose_app_in_browser` enabled so the lab documentation can communicate with Jupyter.
      ```bash
      jupyter lab --expose-app-in-browser
      ```
  1. [OPTIONAL] This can be permanently enabled in the Jupyter configuration.
      ```bash
      mkdir -p ~/.local/etc/jupyter/jupyter_server_config.d
      cat > ~/.local/etc/jupyter/jupyter_server_config.d/jupyterlab.json <<EOF
      {
        "LabApp": {
          "exposeAppInBrowser": true
        }
      }
      EOF
      ```
