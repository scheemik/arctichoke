# Installation

The instructions below show how to get this project set up and running on a new system.
For more details on how the architecture of this project was developed, see the {doc}`Initial Setup <initial_setup>` guide. 

## Contents

- [Installing Podman](#installing-podman)
- [Clone the repository](#clone-the-repository)
- [Specify file paths](#specify-file-paths)
- [Start the container](#start-the-container)

---

## Installing Podman
[back to top](#installation)

Install `podman` following the relevant version of the [Podman Installation Instructions](https://podman.io/docs/installation) for your system.
If running on macOS or Windows, this will necessitate the use of the Podman virtual machine which needs to be active before a container can be run.


## Clone the repository
[back to top](#installation)

Choose a location in which to clone the repository for this project.
```console
user@local:~$ cd /<absolute/path/to/project>
user@local:/<absolute/path/to/project>$ git clone git@github.com:scheemik/seaicecp.git
```


## Specify file paths
[back to top](#installation)

In the `start_container.sh` script, it is important to modify the following lines.
```bash
# ---- Setup external hard drive access ----
export SICP_DATA_DIR=/Volumes/BERGY_BITS/seaicecp_data/
```
Make sure to choose a file path to where you want the data for the project to be saved.
This can, and probably should, be a different location than the project directory.
If you choose an external drive, make sure that drive is connected and mounted before every time you start the container.
When using an external drive, if it is missing when starting the container, you may encounter the following error.
```console
user@local:seaicecp$ bash start_container.sh
Error: vfkit exited unexpectedly with exit code 1
```
If connecting the external drive does not solve that error, check the GitHub issue [Error: vfkit exited unexpectedly with exit code 1 on M4 MacMini #25046](https://github.com/podman-container-tools/podman/issues/25046) for more details.


## Start the container
[back to top](#installation)

Run the `start_container.sh` script to start the container.
The first time this is done, it might take quite a while as it builds the image.
However, once the image is built, the subsequent runs of `start_container.sh` will complete much more quickly as it will be able to simply restart the built image.

<details>

<summary>Expand for example output for running the first time.</summary>

```console
user@local:seaicecp$ bash start_container.sh 
Starting podman machine...
Starting machine "podman-machine-default"

This machine is currently configured in rootless mode. If your containers
require root permissions (e.g. ports < 1024), or if you run into compatibility
issues with non-podman clients, you can switch using the following command:

        podman machine set --rootful

API forwarding listening on: /var/run/docker.sock
Docker API clients default to this address. You do not need to set DOCKER_HOST.

Machine "podman-machine-default" started successfully

[1/2] STEP 1/1: FROM ghcr.io/astral-sh/uv:trixie-slim@sha256:5cbec7ab7753a6c763c6dda6a38f085c8c585ec9f53cfb4e7368b79ca30bc881 AS uv
--> 7a4a3d029284
[2/2] STEP 1/18: FROM debian:trixie-slim@sha256:e18da95f66066b7c5fa31491b524e83121271eca59a3d140f4906c8d0a090367
[2/2] STEP 2/18: ENV DEBIAN_FRONTEND=noninteractive
--> Using cache 3be9c3a94b0331d3dfcf11539db18ba26749fdbe9b631f46c50f49e20980c2b8
--> 3be9c3a94b03
[2/2] STEP 3/18: ENV UV_PROJECT_ENVIRONMENT=/workspace/.cvenv
--> Using cache 41a9dd30080afa814c2cd1be5189c9678acae4ee8e3d9e4405bc8179c5f5f6bd
--> 41a9dd30080a
[2/2] STEP 4/18: ENV UV_LINK_MODE=copy
--> Using cache 100d769d826b5fbbd3152ddf0651d9821b7355c57309616e06c744c0e4e5cb83
--> 100d769d826b
[2/2] STEP 5/18: RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates     curl     git     build-essential     pkg-config     libnetcdf-dev     netcdf-bin     libhdf5-dev     libcurl4-openssl-dev     libssl-dev     cdo     nco     python3.13     python3.13-venv     python3-pip     chromium     chromium-driver     fonts-liberation     && rm -rf /var/lib/apt/lists/*
--> Using cache 0b1c192c6b94df4ea2b025d83485eefafdd06efd69cb289e47a3c9ff07e12619
--> 0b1c192c6b94
[2/2] STEP 6/18: RUN ln -s /usr/bin/python3.13 /usr/bin/python
--> Using cache 67d7c90f3cefad92f10fad5d6fa6916e9b04910b4151254ba475d25acd559093
--> 67d7c90f3cef
[2/2] STEP 7/18: COPY --from=uv /uv /usr/local/bin/uv
--> Using cache 0685ddef98e6d0456ef924f48d21805140aead9f414631ed9815bbc7fc4da86d
--> 0685ddef98e6
[2/2] STEP 8/18: WORKDIR /workspace
--> Using cache ff49bc54bb3111565a740b0753d96d5b34c195db14b14ee00a24448d02ce276c
--> ff49bc54bb31
[2/2] STEP 9/18: COPY pyproject.toml uv.lock ./
--> db02980115ca
[2/2] STEP 10/18: COPY README.md ./
--> e45411fe5602
[2/2] STEP 11/18: COPY src ./src
--> aadbaf0d823b
[2/2] STEP 12/18: RUN --mount=type=cache,target=/root/.cache/uv     uv sync  && uv run python -m ipykernel install --sys-prefix --name python3 --display-name "seaicecp (container)"
Using CPython 3.13.5 interpreter at: /usr/bin/python3
Creating virtual environment at: .cvenv
Resolved 198 packages in 2ms
   Building seaicecp @ file:///workspace
      Built seaicecp @ file:///workspace
Prepared 1 package in 16ms
Installed 195 packages in 8.40s
 + aiofiles==25.1.0
 + aiostream==0.7.1
 + alabaster==1.0.0
 + alembic==1.18.4
 + annotated-types==0.7.0
 + anyio==4.13.0
 + argon2-cffi==25.1.0
 + argon2-cffi-bindings==25.1.0
 + arrow==1.4.0
 + astroid==4.1.2
 + asttokens==3.0.1
 + async-lru==2.3.0
 + attrs==26.1.0
 + babel==2.18.0
 + beautifulsoup4==4.14.3
 + bleach==6.3.0
 + bokeh==3.9.0
 + cartopy==0.25.0
 + cattrs==26.1.0
 + certifi==2026.4.22
 + cffi==2.0.0
 + cftime==1.6.5
 + charset-normalizer==3.4.7
 + click==8.3.3
 + click-params==0.5.0
 + cloudpickle==3.1.2
 + colorcet==3.2.1
 + comm==0.2.3
 + contourpy==1.3.3
 + coverage==7.13.5
 + cryptography==47.0.0
 + cycler==0.12.1
 + dask==2026.3.0
 + debugpy==1.8.20
 + decorator==5.2.1
 + defusedxml==0.7.1
 + deprecated==1.3.1
 + docutils==0.22.4
 + esgpull==0.9.6
 + executing==2.2.1
 + fastjsonschema==2.21.2
 + fonttools==4.62.1
 + fqdn==1.5.1
 + fsspec==2026.4.0
 + geoviews==1.15.1
 + greenlet==3.5.0
 + h11==0.16.0
 + holoviews==1.22.1
 + httpcore==1.0.9
 + httpx==0.28.1
 + hvplot==0.12.2
 + idna==3.13
 + imagesize==2.0.0
 + importlib-metadata==9.0.0
 + iniconfig==2.3.0
 + ipykernel==7.2.0
 + ipython==9.13.0
 + ipython-pygments-lexers==1.1.1
 + ipywidgets==8.1.8
 + isoduration==20.11.0
 + jedi==0.19.2
 + jinja2==3.1.6
 + json5==0.14.0
 + jsonpointer==3.1.1
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 + jupyter==1.1.1
 + jupyter-cache==1.0.1
 + jupyter-client==8.8.0
 + jupyter-console==6.6.3
 + jupyter-core==5.9.1
 + jupyter-events==0.12.1
 + jupyter-lsp==2.3.1
 + jupyter-server==2.17.0
 + jupyter-server-terminals==0.5.4
 + jupyterlab==4.5.6
 + jupyterlab-pygments==0.3.0
 + jupyterlab-server==2.28.0
 + jupyterlab-widgets==3.0.16
 + kiwisolver==1.5.0
 + lark==1.3.1
 + linkify-it-py==2.1.0
 + locket==1.0.0
 + mako==1.3.12
 + markdown==3.10.2
 + markdown-it-py==4.0.0
 + markupsafe==3.0.3
 + matplotlib==3.10.9
 + matplotlib-inline==0.2.1
 + mdit-py-plugins==0.5.0
 + mdurl==0.1.2
 + mistune==3.2.0
 + myst-nb==1.4.0
 + myst-parser==5.0.0
 + narwhals==2.20.0
 + nbclient==0.10.4
 + nbconvert==7.17.1
 + nbformat==5.10.4
 + nest-asyncio==1.6.0
 + netcdf4==1.7.4
 + notebook==7.5.5
 + notebook-shim==0.2.4
 + numpy==2.4.4
 + outcome==1.3.0.post0
 + packaging==26.2
 + pandas==3.0.2
 + pandocfilters==1.5.1
 + panel==1.8.10
 + param==2.3.3
 + parso==0.8.6
 + partd==1.4.2
 + pexpect==4.9.0
 + pillow==12.2.0
 + platformdirs==4.9.6
 + pluggy==1.6.0
 + prometheus-client==0.25.0
 + prompt-toolkit==3.0.52
 + psutil==7.2.2
 + ptyprocess==0.7.0
 + pure-eval==0.2.3
 + pycparser==3.0
 + pydantic==2.13.3
 + pydantic-core==2.46.3
 + pydantic-settings==2.14.0
 + pygments==2.20.0
 + pyopenssl==26.1.0
 + pyparsing==3.3.2
 + pyproj==3.7.2
 + pyshp==3.0.3
 + pysocks==1.7.1
 + pytest==9.0.3
 + pytest-cov==7.1.0
 + python-dateutil==2.9.0.post0
 + python-dotenv==1.2.2
 + python-json-logger==4.1.0
 + pyviz-comms==3.0.6
 + pyyaml==6.0.3
 + pyzmq==27.1.0
 + referencing==0.37.0
 + requests==2.33.1
 + rfc3339-validator==0.1.4
 + rfc3986-validator==0.1.1
 + rfc3987-syntax==1.1.0
 + rich==15.0.0
 + roman-numerals==4.1.0
 + rpds-py==0.30.0
 + seaicecp==0.1.0 (from file:///workspace)
 + selenium==4.43.0
 + send2trash==2.1.0
 + setuptools==82.0.1
 + shapely==2.1.2
 + six==1.17.0
 + sniffio==1.3.1
 + snowballstemmer==3.0.1
 + sortedcontainers==2.4.0
 + soupsieve==2.8.3
 + sphinx==9.1.0
 + sphinx-autoapi==3.8.0
 + sphinx-rtd-theme==3.1.0
 + sphinxcontrib-applehelp==2.0.0
 + sphinxcontrib-devhelp==2.0.0
 + sphinxcontrib-htmlhelp==2.1.0
 + sphinxcontrib-jquery==4.1
 + sphinxcontrib-jsmath==1.0.1
 + sphinxcontrib-qthelp==2.0.0
 + sphinxcontrib-serializinghtml==2.0.0
 + sqlalchemy==2.0.49
 + stack-data==0.6.3
 + tabulate==0.10.0
 + terminado==0.18.1
 + tinycss2==1.4.0
 + tomlkit==0.14.0
 + toolz==1.1.0
 + tornado==6.5.5
 + tqdm==4.67.3
 + traitlets==5.14.3
 + trio==0.33.0
 + trio-websocket==0.12.2
 + typing-extensions==4.15.0
 + typing-inspection==0.4.2
 + tzdata==2026.2
 + uc-micro-py==2.0.0
 + uri-template==1.3.0
 + urllib3==2.6.3
 + validators==0.22.0
 + wcwidth==0.6.0
 + webcolors==25.10.0
 + webencodings==0.5.1
 + websocket-client==1.9.0
 + widgetsnbextension==4.0.15
 + wrapt==2.1.2
 + wsproto==1.3.2
 + xarray==2026.4.0
 + xyzservices==2026.3.0
 + zipp==3.23.1
Installed kernelspec python3 in /workspace/.cvenv/share/jupyter/kernels/python3
--> 05219843dd56
[2/2] STEP 13/18: RUN /workspace/.cvenv/bin/python - <<'EOF' (import cartopy.io.shapereader as shp...)
/workspace/.cvenv/lib/python3.13/site-packages/cartopy/io/__init__.py:242: DownloadWarning: Downloading: https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_coastline.zip
  warnings.warn(f'Downloading: {url}', DownloadWarning)
--> 40d732151a9b
[2/2] STEP 14/18: COPY .devcontainer/esgpull_entrypoint.sh /esgpull_entrypoint.sh
--> 9f5d1fad1e60
[2/2] STEP 15/18: RUN chmod +x /esgpull_entrypoint.sh
--> b7246f666410
[2/2] STEP 16/18: ENTRYPOINT ["/esgpull_entrypoint.sh"]
--> f14e0bf22957
[2/2] STEP 17/18: EXPOSE 8888
--> a5f4f112906c
[2/2] STEP 18/18: CMD ["bash", "-lc", "exec uv run jupyter lab     --ip=0.0.0.0     --port=8888     --no-browser     --allow-root     --ServerApp.token=''     --ServerApp.password=''"]
[2/2] COMMIT seaicecp_7
--> 27f0309d397f
Successfully tagged localhost/seaicecp_7:latest
27f0309d397f573599f2449782ada3e82a4ff9a55f6a12c71ac47f511726610f

──────────────────────────────────── esgpull installation ────────────────────────────────────
Creating install directory and files at /seaicecp_data/bergybits
Install config added to /root/.config/esgpull/installs.json
      Built seaicecp @ file:///workspace
Uninstalled 1 package in 13ms
Installed 1 package in 62ms
[I 2026-06-04 18:23:25.915 ServerApp] jupyter_lsp | extension was successfully linked.
[I 2026-06-04 18:23:25.925 ServerApp] jupyter_server_terminals | extension was successfully linked.
[I 2026-06-04 18:23:25.934 ServerApp] jupyterlab | extension was successfully linked.
[I 2026-06-04 18:23:25.946 ServerApp] notebook | extension was successfully linked.
[I 2026-06-04 18:23:25.948 ServerApp] Writing Jupyter server cookie secret to /root/.local/share/jupyter/runtime/jupyter_cookie_secret
[I 2026-06-04 18:23:27.822 ServerApp] notebook_shim | extension was successfully linked.
[I 2026-06-04 18:23:27.823 ServerApp] panel.io.jupyter_server_extension | extension was successfully linked.
[W 2026-06-04 18:23:27.959 ServerApp] All authentication is disabled.  Anyone who can connect to this server will be able to run code.
[I 2026-06-04 18:23:27.960 ServerApp] notebook_shim | extension was successfully loaded.
[I 2026-06-04 18:23:27.966 ServerApp] jupyter_lsp | extension was successfully loaded.
[I 2026-06-04 18:23:27.968 ServerApp] jupyter_server_terminals | extension was successfully loaded.
[I 2026-06-04 18:23:28.012 LabApp] JupyterLab extension loaded from /workspace/.cvenv/lib/python3.13/site-packages/jupyterlab
[I 2026-06-04 18:23:28.012 LabApp] JupyterLab application directory is /workspace/.cvenv/share/jupyter/lab
[I 2026-06-04 18:23:28.017 LabApp] Extension Manager is 'pypi'.
[I 2026-06-04 18:23:28.366 ServerApp] jupyterlab | extension was successfully loaded.
[I 2026-06-04 18:23:28.403 ServerApp] notebook | extension was successfully loaded.
[I 2026-06-04 18:23:28.404 ServerApp] panel.io.jupyter_server_extension | extension was successfully loaded.
[I 2026-06-04 18:23:28.406 ServerApp] Serving notebooks from local directory: /workspace
[I 2026-06-04 18:23:28.406 ServerApp] Jupyter Server 2.17.0 is running at:
[I 2026-06-04 18:23:28.406 ServerApp] http://e343a4f95781:8888/lab
[I 2026-06-04 18:23:28.406 ServerApp]     http://127.0.0.1:8888/lab
[I 2026-06-04 18:23:28.406 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[I 2026-06-04 18:23:28.620 ServerApp] Skipped non-installed server(s): basedpyright, bash-language-server, dockerfile-language-server-nodejs, javascript-typescript-langserver, jedi-language-server, julia-language-server, pyrefly, pyright, python-language-server, python-lsp-server, r-languageserver, sql-language-server, texlab, typescript-language-server, unified-language-server, vscode-css-languageserver-bin, vscode-html-languageserver-bin, vscode-json-languageserver-bin, yaml-language-server
```

</details>

If the script executed with no errors, you will see output indicating that a Jupyter server is running.
The next step would be to follow the instructions on {doc}`Testing the container's Jupyter server <jupyter_test>`