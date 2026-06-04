# Starting the Container

This is a short guide showing how to start the container for the project which assumes you have already followed the {doc}`Installation <installation>` page.
For details on how the container was developed, see the {doc}`Initial Setup <initial_setup>` page.

The script called `start_container.sh` will ultimately start the container for this project, but first it checks to make sure the Podman virtual machine is running (if on macOS or Windows) and whether the image for this project needs to be built or rebuilt.

This script can be run with a simple `bash` command.
```console
Grey@Audron:seaicecp$ bash start_container.sh 
Starting podman machine...
Starting machine "podman-machine-default"

This machine is currently configured in rootless mode. If your containers
require root permissions (e.g. ports < 1024), or if you run into compatibility
issues with non-podman clients, you can switch using the following command:

        podman machine set --rootful

API forwarding listening on: /var/run/docker.sock
Docker API clients default to this address. You do not need to set DOCKER_HOST.

Machine "podman-machine-default" started successfully
───────────────────────────────────────────────────── esgpull installation ──────────────────────────────────────────────────────
Using existing install at /seaicecp_data/bergybits
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
...
```
Leave this terminal running to have access to the Jupyter server and see relevant updates.
