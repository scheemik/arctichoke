<a id='top'></a>
# Initial Setup

This guide details how the architecture of this project was developed.
For streamlined instructions on how to install and start using this project, see the {doc}`Installation <installation>` page.

The structure of this project is based on the incredibly helpful guide, [Python Packages](https://py-pkgs.org/welcome).
Several of the sections below are summarizations of parts of that guide, with details of the changes I made for this specific setup. 

## Contents

- [The Order of Operations](#order_of_operations)
- [The `uv` package manager](#uv_manager)
- [Creating a package structure](#pkg_structure)
    - [Using `uv init`](#uv_init)
    - [Using a `cookiecutter` template](#cookiecutter)
    - [Combining `uv` and `cookiecutter` structures](#uv_and_cookiecutter)
- [Version control and GitHub](#version_control)
    - [Setting the default branch](#default_branch)
- [Podman](#podman)
    - [Installing Podman](#podman_install)
    - [Testing Podman](#podman_test)
    - [Pod Manager extension for VSCodium](#pod_manager_extension)
    - [Building a simple container](#podman_simple_container)
    - [The Containerfile](#podman_containerfile)
        - [Pinning the versions of `uv` and `trixie-slim`](#podman_containerfile_pin_versions)
        - [Defining environment variables](#podman_containerfile_env_vars)
        - [Installing system and scientific dependencies](#podman_containerfile_apt-get)
        - [Preparing Python, `uv`, and working directory](#podman_containerfile_misc_prep)
        - [`uv` dependencies and Jupyter kernel](#podman_containerfile_uv_jupyter)
        - [Download commonly used Natural Earth shapefiles](#podman_containerfile_natural_earth)
        - [Set up `esgpull` install](#podman_containerfile_esgpull)
        - [Set up the Jupyter server](#podman_containerfile_jupyter_server)
    - [The `start_container` script](#podman_start_container)
        - [Set the script to fail on common errors](#podman_start_container_pipefail)
        - [Ensure the virtual machine is running](#podman_start_container_machine_status)
        - [Set the parameters](#podman_start_container_params)
        - [Check existing containers and images](#podman_start_container_cleanup)
        - [Set up access to external volumes](#podman_start_container_external_vol)
        - [Create the list of volumes](#podman_start_container_list_vol)
        - [Run the container](#podman_start_container_run)
- [Virtual environment and packages](#venv)
    - [Activating the virtual environment](#venv_activate)
    - [Adding package dependencies](#venv_dependencies)
    - [Adding `esgpull`](#esgpull)
        - [Adding `esgpull` install on an external drive](#esgpull_ext_HD)
    - [Using a Jupyter notebook](#jupyter_notebook)
    - [Adding `cdo`](#cdo_install)
- [Building the package](#build_pkg)
- [Documentation](#docs)
    - [Building documentation](#build_docs)
    - [Hosting documentation](#host_docs)
    - [Enabling $\LaTeX$ math syntax](#latex_syntax)
    - [Enabling easy DOI links](#doi_links)

---
<a id='order_of_operations'></a>
[back to top](#top)

## The Order of Operations

When initially setting up this project, I installed the [`uv` package manager](#uv_manager), [created the package structure](#pkg_structure) of the project, and [installed Python dependencies in a virtual environment](#venv) all before writing the [Podman](#podman) container.
It is likely that one could avoid installing `uv` on their host system by first setting up the container and, once inside the container, create the package structure.
However, I present those steps first as I have not tested that possibility and thus present them in the manner I followed, outside the container.
I do, however, place the section on the [virtual environment and installing package dependencies](#venv) after creating the container in this document because I have confirmed that adding packages with `uv` inside the container works.

---
<a id='uv_manager'></a>
[back to top](#top)

## The `uv` Package Manager

In [Python Packages Chapter 2](https://py-pkgs.org/02-setup), they suggest to use Miniconda to create an environment and use [`poetry`](https://python-poetry.org/) to manage dependencies. 
For this project, I decided to use [`uv`](https://docs.astral.sh/uv/) instead. 
From the instructions for [Installing `uv`](https://docs.astral.sh/uv/getting-started/installation/), I used Homebrew.
I've truncated the output below for brevity. 
```console
Grey@Audron:~$ brew install uv
==> Auto-updating Homebrew...
Adjust how often this is run with `$HOMEBREW_AUTO_UPDATE_SECS` or disable with
`$HOMEBREW_NO_AUTO_UPDATE=1`. Hide these hints with `$HOMEBREW_NO_ENV_HINTS=1` (see `man brew`).
==> Downloading https://ghcr.io/v2/homebrew/core/portable-ruby/blobs/sha256:7c7830166a509857669c544dcba7a0d08ca656a3da073c68826ca0a5b1b56b12
################################################################################################################ 100.0%
==> Pouring portable-ruby-4.0.2_1.catalina.bottle.tar.gz
==> Auto-updated Homebrew!
Updated 2 taps (homebrew/core and homebrew/cask).
...
==> Summary
🍺  /usr/local/Cellar/uv/0.11.6: 17 files, 54.0MB
```

I then ensured that I had the most up-to-date version of `uv` installed.
```console
Grey@Audron:~$ brew upgrade uv
Warning: uv 0.11.6 already installed
```


---
<a id='pkg_structure'></a>
[back to top](#top)

## Creating a package structure

<a id='uv_init'></a>
[back to top](#top)

### Using `uv init`

To start a project, I simply need to use `uv` to initiate one, following the [Working on projects](https://docs.astral.sh/uv/guides/projects/) guide.
I chose the name `seaicecp` to stand for "Sea Ice Choke Points," trying to balance brevity and descriptiveness.
First, I navigated to the directory in which I want my project to be, `<absolute/path/to/project>`, then used the `uv init` command with the name for the project and the `--package` flag.
```console
Grey@Audron:~$ cd /<absolute/path/to/project>
Grey@Audron:/<absolute/path/to/project>$ uv init seaicecp --package
Initialized project `seaicecp` at `/<absolute/path/to/project>/seaicecp`
```

This creates a very simple directory structure for the project.
```console
Grey@Audron:/<absolute/path/to/project>$ tree seaicecp
├── .gitignore
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```

<a id='cookiecutter'></a>
[back to top](#top)

### Using a `cookiecutter` template

In [Py-Pkgs Section 2.2.2](https://py-pkgs.org/02-setup#install-packaging-software), they suggest installing `cookiecutter` to create a package from a pre-made template. 
This package is then actually used in [Section 3.2.2](https://py-pkgs.org/03-how-to-package-a-python#creating-a-package-structure). 
I do like the package structure they provide with their `cookiecutter` template, but I will need to integrate it with the directory structure generated above with `uv init` as their template assumes using `poetry` as a dependency manager.

`uv` comes the ability to [invoke a tool without installing it by using `uvx`](https://docs.astral.sh/uv/guides/tools/#running-tools). 
This is helpful when trying something out, or when using a tool that is just for an initial set up, like [`cookiecutter`](https://github.com/cookiecutter/cookiecutter), which can be used to create a package structure.
By using `uvx`, you don't need to commit to actually installing `cookiecutter` on your system.

First, I created and went into a temporary directory, `tmp_dir`, then generated the package structure.
This is to ensure I didn't accidentally overwrite the structure I made with `uv init` earlier.
```console
Grey@Audron:seaicecp$ mkdir tmp_dir
Grey@Audron:seaicecp$ cd tmp_dir
Grey@Audron:tmp_dir$ git branch -m master main
$ uvx cookiecutter https://github.com/py-pkgs/py-pkgs-cookiecutter.git
Installed 21 packages in 137ms
  [1/7] author_name (Monty Python): Mikhail Schee
  [2/7] package_name (mypkg): seaicecp
  [3/7] package_short_description (A package for doing great things!): Investigate sea ice choke points in the Canadian Arctic Archipelago using high-resolution models.
  [4/7] package_version (0.1.0): 
  [5/7] python_version (3.12): 3.13.5
  [6/7] Select open_source_license
    1 - MIT
    2 - Apache License 2.0
    3 - GNU General Public License v3.0
    4 - CC0 v1.0 Universal
    5 - BSD 3-Clause
    6 - Proprietary
    7 - None
    Choose from [1/2/3/4/5/6/7] (1): 
  [7/7] Select include_github_actions
    1 - no
    2 - ci
    3 - ci+cd
    Choose from [1/2/3] (1):
```

This generates a directory with the chosen package name (in this case, `seaicecp`) and fill it with all the boiler-plate files you would expect in a Python Package.
```console
Grey@Audron:tmp_dir$ tree seaicecp/
seaicecp/
├── CHANGELOG.md
├── CONDUCT.md
├── CONTRIBUTING.md
├── docs
│   ├── changelog.md
│   ├── conduct.md
│   ├── conf.py
│   ├── contributing.md
│   ├── example.ipynb
│   ├── index.md
│   ├── make.bat
│   ├── Makefile
│   └── requirements.txt
├── LICENSE
├── pyproject.toml
├── README.md
├── src
│   └── seaicecp
│       ├── __init__.py
│       └── seaicecp.py
└── tests
    └── test_seaicecp.py

5 directories, 18 files
```

<a id='uv_and_cookiecutter'></a>
[back to top](#top)

### Combining `uv` and `cookiecutter` structures

Below are the files that are shared across both structures I generated and what changes I needed to make.
- The `src/` directory
    - Use the version generated by the `cookiecutter`.
- `.gitignore`
    - Use the version generated by the `cookiecutter` as it is more extensive.
- `README.md`
    - Use the version generated by the `cookiecutter` as the one generated by `uv init` will be blank.
- `pyproject.toml`
    - Use the version generated by `uv init` as a base.
    - Copy in the lines from the `cookiecutter` version that start with:
        - `description`
        - `authors`
        - `license`

The `pyproject.toml` file initially looks like:
```toml
[project]
name = "seaicecp"
version = "0.1.0"
description = "Investigate sea ice choke points in the Canadian Arctic Archipelago using high-resolution models."
authors = [
    { name = "Mikhail Schee", email = "mikhail.schee@alumni.utoronto.ca" }
]
license = "MIT"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    
]

[dependency-groups]
dev = [
    "ipykernel>=7.2.0",
]

[project.scripts]
seaicecp = "seaicecp:main"

[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
build-backend = "uv_build"
```

After completing those steps, I deleted the redundant instance of my project directory in `tmp_dir`. 
```console
Grey@Audron:tmp_dir$ cd ..
Grey@Audron:seaicecp$ rm -rf tmp_dir/
```

<a id='version_control'></a>
[back to top](#top)

## Version control and GitHub

Following [Py-Pkgs Section 3.3. Put your package under version control](https://py-pkgs.org/03-how-to-package-a-python#put-your-package-under-version-control), I initiated `git` for my new repository.
```console
Grey@Audron:seaicecp$ git init
Initialized empty Git repository in /<absolute/path/to/project>/seaicecp/.git/
```

I then added and committed the initial structure and pushed to a new [GitHub repository for the project](https://github.com/scheemik/seaicecp).
I am working in VSCodium, which I'd already set up to [connect to my GitHub account](https://github.com/VSCodium/vscodium/blob/master/docs/usage.md#signin-github), so the process was as simple as pressing the "push" button in the GUI.

<a id='default_branch'></a>
[back to top](#top)

### Setting the default branch

For the version of `git` I have, it still sets the default branch as `master` instead of `main`. 
I'm following the guide from Geeks for Geeks on [How to Change Git Default Branch From Master?](https://www.geeksforgeeks.org/git/how-to-change-git-default-branch-from-master/)

First, I renamed the local branch.
```console
Grey@Audron:/<absolute/path/to/project>$ cd seaicecp
Grey@Audron:seaicecp$ git branch -m master main
Grey@Audron:seaicecp$ git push -u origin main
Total 0 (delta 0), reused 0 (delta 0)
remote: 
remote: Create a pull request for 'main' on GitHub by visiting:
remote:      https://github.com/scheemik/seaicecp/pull/new/main
remote: 
To https://github.com/scheemik/seaicecp.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

Then, on GitHub, I went to the "Settings" tab for the repository, then confirmed I was in the "General" section on the sidebar.
Under the heading "Default branch," I clicked the button to "Switch to another branch," selected `main`, then hit "Update."
Next, I deleted the `master` branch from the remote.
```console
Grey@Audron:seaicecp$ git push origin --delete master
To https://github.com/scheemik/seaicecp.git
 - [deleted]         master
```

Since the repository had not been cloned anywhere else at this point, that was all I needed to do.

---
<a id='podman'></a>
[back to top](#top)

## Podman

[Podman](https://podman.io/) is an open-source tool by [Red Hat](https://www.redhat.com/en0) for creating and managing containers, similar to [Docker](https://www.docker.com/).
[Containerization](https://en.wikipedia.org/wiki/Containerization_(computing)) allows the creation of isolated, reproducible computing environments, making it easier to ensure code will run the same way across different systems.
While virtual environments for Python, such as [`venv`](https://docs.python.org/3/library/venv.html) or [`conda`](https://www.anaconda.com/download), create reproducible environments for Python packages, containers create reproducible environments for an entire operating system.
This allows the inclusion and management of non-Python software in a project, such as the `cdo` and `esgpull` tools used in this project.

<a id='podman_install'></a>
[back to top](#top)

### Installing Podman
<!-- See GPBS_Log 2026/04/28 -->

I installed `podman` on my MacBook following the [Podman Installation Instructions](https://podman.io/docs/installation). 
I downloaded the `podman-installer-macos-universal.pkg` version from the [`podman` GitHub latest release (v5.8.2) page](https://github.com/containers/podman/releases). 
Opening that brought me through the familiar GUI software installation process common to many applications for macOS. 
I agreed to the [license](https://www.apache.org/licenses/), selected which users for whom I will install it, then watched the loading bar. 
It took less than a minute. 

This process also added an item from "Red Hat" in Settings -> Login Items & Extensions -> Allow in the Background. 
I assume this is necessary for this to actually run properly. 
I then moved the `.pkg` file to the trash.

The next step in the [Podman Installation Instructions](https://podman.io/docs/installation) for macOS is to setup the Podman virtual machine.
This is necessary when running Podman on macOS or Windows as it needs to run on a Linux system, therefore I need to initialize a virtual machine to actually run Podman.
```console
Grey@Audron:~$ podman machine init
Looking up Podman Machine image at quay.io/podman/machine-os:5.8 to create VM
Getting image source signatures
Copying blob 5efcf56a5999 done   | 
Copying config 44136fa355 done   | 
Writing manifest to image destination
5efcf56a599919c786136faf8e4f48b25bf3865b5e8ea3302f6d705ba750afec
Extracting compressed file: podman-machine-default-amd64.raw: done  
Machine init complete
To start your machine run:

	podman machine start
```
That took about 3 minutes.
Next, I started the virtual machine.
```console
Grey@Audron:~$ podman machine start
Starting machine "podman-machine-default"

This machine is currently configured in rootless mode. If your containers
require root permissions (e.g. ports < 1024), or if you run into compatibility
issues with non-podman clients, you can switch using the following command:

	podman machine set --rootful

API forwarding listening on: /var/run/docker.sock
Docker API clients default to this address. You do not need to set DOCKER_HOST.

Machine "podman-machine-default" started successfully
```
That took about a minute. 
Then, I took a look at the `podman` information.
There is quite a lot of information, so I'll collapse most of the output.
```console
Grey@Audron:~$ podman info
Client:
  APIVersion: 5.8.2
  BuildOrigin: pkginstaller
  Built: 1776189122
  BuiltTime: Tue Apr 14 13:52:02 2026
  GitCommit: 5b263b5f5b48004a87caac44e67349a8266d9ef4
  GoVersion: go1.26.2
  Os: darwin
  OsArch: darwin/amd64
  Version: 5.8.2
...
```
<details>

<summary>Expand for more output</summary>

```console
...
host:
  arch: amd64
  buildahVersion: 1.43.1
  cgroupControllers:
  - cpu
  - io
  - memory
  - pids
  cgroupManager: systemd
  cgroupVersion: v2
  conmon:
    package: conmon-2.2.1-2.fc43.x86_64
    path: /usr/bin/conmon
    version: 'conmon version 2.2.1, commit: '
  cpuUtilization:
    idlePercent: 92.76
    systemPercent: 4.49
    userPercent: 2.75
  cpus: 4
  databaseBackend: sqlite
  distribution:
    distribution: fedora
    variant: coreos
    version: "43"
  emulatedArchitectures:
  - linux/arm64
  - linux/arm64be
  eventLogger: journald
  freeLocks: 2048
  hostname: localhost.localdomain
  idMappings:
    gidmap:
    - container_id: 0
      host_id: 1000
      size: 1
    - container_id: 1
      host_id: 100000
      size: 1000000
    uidmap:
    - container_id: 0
      host_id: 502
      size: 1
    - container_id: 1
      host_id: 100000
      size: 1000000
  kernel: 6.19.7-200.fc43.x86_64
  linkmode: dynamic
  logDriver: journald
  memFree: 1404866560
  memTotal: 2046451712
  networkBackend: netavark
  networkBackendInfo:
    backend: netavark
    defaultNetwork: podman
    dns:
      package: aardvark-dns-1.17.0-1.fc43.x86_64
      path: /usr/libexec/podman/aardvark-dns
      version: aardvark-dns 1.17.0
    package: netavark-1.17.2-1.fc43.x86_64
    path: /usr/libexec/podman/netavark
    version: netavark 1.17.2
  ociRuntime:
    name: crun
    package: crun-1.25.1-1.fc43.x86_64
    path: /usr/bin/crun
    version: |-
      crun version 1.25.1
      commit: 156ae065d4a322d149c7307034f98d9637aa92a2
      rundir: /run/user/502/crun
      spec: 1.0.0
      +SYSTEMD +SELINUX +APPARMOR +CAP +SECCOMP +EBPF +CRIU +LIBKRUN +WASM:wasmedge +YAJL
  os: linux
  pasta:
    executable: /usr/bin/pasta
    package: passt-0^20260120.g386b5f5-1.fc43.x86_64
    version: |
      pasta 0^20260120.g386b5f5-1.fc43.x86_64
      Copyright Red Hat
      GNU General Public License, version 2 or later
        <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>
      This is free software: you are free to change and redistribute it.
      There is NO WARRANTY, to the extent permitted by law.
  remoteSocket:
    exists: true
    path: unix:///run/user/502/podman/podman.sock
  rootlessNetworkCmd: pasta
  security:
    apparmorEnabled: false
    capabilities: CAP_CHOWN,CAP_DAC_OVERRIDE,CAP_FOWNER,CAP_FSETID,CAP_KILL,CAP_NET_BIND_SERVICE,CAP_SETFCAP,CAP_SETGID,CAP_SETPCAP,CAP_SETUID,CAP_SYS_CHROOT
    rootless: true
    seccompEnabled: true
    seccompProfilePath: /usr/share/containers/seccomp.json
    selinuxEnabled: true
  serviceIsRemote: true
  slirp4netns:
    executable: /usr/bin/slirp4netns
    package: slirp4netns-1.3.1-3.fc43.x86_64
    version: |-
      slirp4netns version 1.3.1
      commit: e5e368c4f5db6ae75c2fce786e31eef9da6bf236
      libslirp: 4.9.1
      SLIRP_CONFIG_VERSION_MAX: 6
      libseccomp: 2.6.0
  swapFree: 0
  swapTotal: 0
  uptime: 0h 1m 23.00s
  variant: ""
plugins:
  authorization: null
  log:
  - k8s-file
  - none
  - passthrough
  - journald
  network:
  - bridge
  - macvlan
  - ipvlan
  volume:
  - local
registries:
  search:
  - docker.io
store:
  configFile: /var/home/core/.config/containers/storage.conf
  containerStore:
    number: 0
    paused: 0
    running: 0
    stopped: 0
  graphDriverName: overlay
  graphOptions: {}
  graphRoot: /var/home/core/.local/share/containers/storage
  graphRootAllocated: 106769133568
  graphRootUsed: 4263370752
  graphStatus:
    Backing Filesystem: xfs
    Native Overlay Diff: "true"
    Supports d_type: "true"
    Supports shifting: "false"
    Supports volatile: "true"
    Using metacopy: "false"
  imageCopyTmpDir: /var/tmp
  imageStore:
    number: 0
  runRoot: /run/user/502/containers
  transientStore: false
  volumePath: /var/home/core/.local/share/containers/storage/volumes
...
```

</details>

```console
...
version:
  APIVersion: 5.8.2
  BuildOrigin: 'Copr: packit/containers-podman-28501'
  Built: 1776038400
  BuiltTime: Sun Apr 12 20:00:00 2026
  GitCommit: 5b263b5f5b48004a87caac44e67349a8266d9ef4
  GoVersion: go1.25.9 X:nodwarf5
  Os: linux
  OsArch: linux/amd64
  Version: 5.8.2
```

I can also simply check the version of `podman`.
```console
Grey@Audron:~$ podman version
Client:        Podman Engine
Version:       5.8.2
API Version:   5.8.2
Go Version:    go1.26.2
Git Commit:    5b263b5f5b48004a87caac44e67349a8266d9ef4
Built:         Tue Apr 14 13:52:02 2026
Build Origin:  pkginstaller
OS/Arch:       darwin/amd64

Server:       Podman Engine
Version:      5.8.2
API Version:  5.8.2
Go Version:   go1.25.9 X:nodwarf5
Git Commit:   5b263b5f5b48004a87caac44e67349a8266d9ef4
Built:        Sun Apr 12 20:00:00 2026
OS/Arch:      linux/amd64
```
I can also see that I now have `podman` files in my user's configuration folder.
```console
Grey@Audron:~$ ls -la ~/.config/containers/
total 8
drwxr-xr-x  5 Grey  staff  160 Apr 28 10:57 .
drwx------  8 Grey  staff  256 Apr 28 10:55 ..
drwxr-xr-x  3 Grey  staff   96 Apr 28 10:55 podman
-rw-r--r--  1 Grey  staff  440 Apr 28 10:57 podman-connections.json
-rw-r--r--  1 Grey  staff    0 Apr 28 10:57 podman-connections.json.lock
```
<a id='podman_test'></a>
[back to top](#top)

---

### Testing Podman

Next, I followed the [Basic Setup and Use of Podman](https://github.com/containers/podman/blob/main/docs/tutorials/podman_tutorial.md) guide.
To start, I ran the sample `nginx` container, calling it `basic_httpd`.
```console
Grey@Audron:~$ podman run --name basic_httpd -d -p 8080:80/tcp docker.io/nginx
Trying to pull docker.io/library/nginx:latest...
Getting image source signatures
Copying blob sha256:677c631968686eeb23ab8dd436d49bde041266df5d8952f03d7a8c418643d4b5
Copying blob sha256:ce776bbcda0d6bf4da8df324b82066a03f45bfbbbe520df535293ae069994e84
Copying blob sha256:4677c2a9a3d4f9290cb784d95a9e16378655ecdd7df9e77668d3915262730d0b
Copying blob sha256:85c66128325abc04138f6944d943e5279375665f6dbefe7f4f6b5e9646d31998
Copying blob sha256:ff048f1f2159a060f69b1861ea262b839cc6e77a9389848929f70275eb7c9e29
Copying blob sha256:3531af2bc2a9c8883754652783cf96207d53189db279c9637b7157d034de7ecd
Copying blob sha256:801a1ad15b4e00add388aca409568400fb8071019d6ba83995f43170af7656fe
Copying config sha256:6c3a6ea6608c89c79027066654a2ef4f0fe58a7bf2c08cc3894733406e476602
Writing manifest to image destination
774a97cf2828429b1feeddae152869417a57cbdcc1e13c0b97ba777aafc762fc
```
This pulls the image from the web, builds it, and starts a container running that image.
If the above command is run a second time, it will be able to skip the part where it downloads and builds the image.
I can now list my running containers.
```console
Grey@Audron:~$ podman ps -a
CONTAINER ID  IMAGE                           COMMAND               CREATED             STATUS             PORTS                 NAMES
774a97cf2828  docker.io/library/nginx:latest  nginx -g daemon o...  About a minute ago  Up About a minute  0.0.0.0:8080->80/tcp  basic_httpd
```
Adding the `-a` flag shows "all" containers, but that doesn't result in any different output than without it at this moment because I just have the one container.

Then, I can inspect that running container.
```console
Grey@Audron:~$ podman inspect basic_httpd | grep IPAddress
               "IPAddress": "10.88.0.3",
                         "IPAddress": "10.88.0.3",
```
This is different than what is shown in the guide which says:
> "As the container is running in rootless mode, an IP address is not assigned and the value will be listed as 'none' in the output from inspect." 

<!-- So, I'm not sure if I am running rootless or not as I did, in fact, get an IP address. -->

Next, I tested the `httpd` server to make sure it is running on the expected port, displaying the index page.
```console
Grey@Audron:~$ curl http://localhost:8080
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, nginx is successfully installed and working.
Further configuration is required for the web server, reverse proxy, 
API gateway, load balancer, content cache, or other features.</p>

<p>For online documentation and support please refer to
<a href="https://nginx.org/">nginx.org</a>.<br/>
To engage with the community please visit
<a href="https://community.nginx.org/">community.nginx.org</a>.<br/>
For enterprise grade support, professional services, additional 
security features and capabilities please refer to
<a href="https://f5.com/nginx">f5.com/nginx</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```
Using the Container ID from the `podman ps` command above, I can see the logs of this container.
```console
Grey@Audron:~$ podman logs 774a97cf2828
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/04/28 15:13:47 [notice] 1#1: using the "epoll" event method
2026/04/28 15:13:47 [notice] 1#1: nginx/1.29.8
2026/04/28 15:13:47 [notice] 1#1: built by gcc 14.2.0 (Debian 14.2.0-19) 
2026/04/28 15:13:47 [notice] 1#1: OS: Linux 6.19.7-200.fc43.x86_64
2026/04/28 15:13:47 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 524288:524288
2026/04/28 15:13:47 [notice] 1#1: start worker processes
2026/04/28 15:13:47 [notice] 1#1: start worker process 24
2026/04/28 15:13:47 [notice] 1#1: start worker process 25
2026/04/28 15:13:47 [notice] 1#1: start worker process 26
2026/04/28 15:13:47 [notice] 1#1: start worker process 27
10.88.0.2 - - [28/Apr/2026:15:21:21 +0000] "GET / HTTP/1.1" 200 896 "-" "curl/8.7.1" "-"
```
I can also see the `httpd pid` with `top` using the same container ID.
```console
Grey@Audron:~$ podman top 774a97cf2828
USER      PID     PPID    %CPU    ELAPSED           TTY     TIME    COMMAND
root      1       0       0.000   10m43.083334622s  ?       0s      nginx: master process nginx -g daemon off;
nginx     24      1       0.000   10m42.083710443s  ?       0s      nginx: worker process
nginx     25      1       0.000   10m42.083812615s  ?       0s      nginx: worker process
nginx     26      1       0.000   10m42.083879016s  ?       0s      nginx: worker process
nginx     27      1       0.000   10m42.083942087s  ?       0s      nginx: worker process
```
<!-- [Checkpointing podman containers](https://podman.io/docs/checkpoint) is only available with root containers, so I'm going to skip that for now. -->

Next, I'll be following part of the guide [How to run your first rootless container with Podman](https://cloudqubes.com/letters/how-to-run-your-first-rootless-container-with-podman).
One of the benefits of Podman is the ability to run containers as "rootless" which adds an extra layer of security. 
The `podman exec <container_name>` command allows you to execute commands within a container.
I will use this to execute the `whoami` command to ask who the container thinks they are.
```console
Grey@Audron:~$ podman exec basic_httpd whoami
root
```
So, the container is running as `root`. 
Next, I'll see who owns the process.
```console
Grey@Audron:~$ podman top basic_httpd user huser
USER        HUSER
root        502
nginx       100100
nginx       100100
nginx       100100
nginx       100100
```
I can see here that the user id between `root` and the `nginx` container don't match, so it seems like that confirms that even though, inside the container, the service is running as `root`, outside the container, it is not.

Next, I can stop the container.
```console
Grey@Audron:~$ podman stop basic_httpd
basic_httpd
```
Then, I'll remove this container and check to make sure it is gone.
```console
Grey@Audron:~$ podman rm basic_httpd
basic_httpd
Grey@Audron:~$ podman ps -a
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES
```

<a id='pod_manager_extension'></a>
[back to top](#top)

---

### Pod Manager extension for VSCodium

I went to VSCodium and installed the "Pod Manager" extension from user `dreamcatcher45`. 
When I first went into the extension, I got the following error:
```console
Failed to get containers: Error: Command failed: podman container ls -a --format "{{.ID}}|{{.Names}}|{{.Status}}|{{.Labels}}"
/bin/sh: podman: command not found
```
I figured out that VSCodium had been open since before I installed `podman`, and I couldn't actually run `podman version` in the VSCodium terminal panel. 
After I restarted VSCodium, both the `podman version` command and the Pod Manager extension worked.

In the sidebar of VSCodium, I clicked on the Pod Manger icon, which looks like a stylized seal.
Currently, the dropdown for "Containers" is empty because I remove the ones I was testing above.
However, under the "Images" dropdown, I see "docker.io/library/nginx:latest (7aaca76c508f)."
This is the image that was built when [Testing Podman](#podman_test).

Containers get added to the list in the Pod Manager sidebar when they start running. 
I can start the `basic_httpd` container again.
```console
Grey@Audron:seaicecp$ podman run --name basic_httpd -d -p 8080:80/tcp docker.io/nginx
9ab04fb2f7c04e2a1cf263ee46b33a00cde5fc7c89e71926f7a65aeae4e35dd7
```
Since this image was already built, all that needed to be done was start a container with the image.
Hitting the refresh button next to the overall "Resources" dropdown at the top of the Pod Manager sidebar reveals this `basic_httpd` container. 
The container name has a long alphanumeric string in parentheses appended which changes every time the container is started.

When hovering over the name of the container, several options appear.
One of these is to "Open in Terminal" which does the equivalent of opening a new terminal inside VSCodium and entering the container, all in one click.
From there, commands can be executed inside the container.
```console
podman exec -it 9ab04fb2f7c0 /bin/sh

The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
Grey@Audron:seaicecp$ podman exec -it 9ab04fb2f7c0 /bin/sh
# basic_httpd whoami
root
# 
```
Then, to clean up, I will stop and remove this `basic_httpd` from outside the container.
```console
Grey@Audron:~$ podman stop basic_httpd
basic_httpd
Grey@Audron:~$ podman rm basic_httpd
basic_httpd
Grey@Audron:~$ podman ps -a
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES
```
If any terminals had been left open inside the container, they will have automatically exited when the container is removed.

<a id='podman_simple_container'></a>
[back to top](#top)

---

### Building a simple container

Above, I downloaded an existing image `docker.io/nginx` from a repository. 
For this project, I want to define my own.
The setup of a container is defined by a scripted that is named `Containerfile` with no file extension. 
A good way to start a container is to load an existing minimal distribution.
I chose the `trixie-slim` version of Debian as it is lightweight and [uses Python 3.13 by default](https://packages.debian.org/trixie/python3).

In [Python Packages Chapter 2](https://py-pkgs.org/02-setup), they suggest using Miniconda to create an environment and the [`poetry`](https://python-poetry.org/) package to manage dependencies. 
For this project, I decided to use [`uv`](https://docs.astral.sh/uv/) instead as it has the ability to manage tools and add ephemeral packages when testing out builds.

I can create a minimal `Containerfile` to test running `trixie-slim` with Python 3.13 and `uv` installed.
```dockerfile
# ---- Stage 1: get uv binary ----
FROM ghcr.io/astral-sh/uv:latest AS uv

# ---- Stage 2: main image ----
FROM debian:trixie-slim

ENV DEBIAN_FRONTEND=noninteractive

# ---- System dependencies ----
RUN apt-get update && apt-get install -y python3.13 

# ---- Make python command available ----
RUN ln -s /usr/bin/python3.13 /usr/bin/python

# ---- Copy uv from official image ----
COPY --from=uv /uv /usr/local/bin/uv

# ---- Set working directory ----
WORKDIR /workspace

# Default shell
CMD ["/bin/bash"]
```
Next, I'll build the image.
A lot of information is output to the console in the build process, so I'll collapse most of the output for brevity.
```console
Grey@Audron:seaicecp$ podman build -f Containerfile -t test_trixie .
[1/2] STEP 1/1: FROM ghcr.io/astral-sh/uv:latest AS uv
Trying to pull ghcr.io/astral-sh/uv:latest...
Getting image source signatures
Copying blob sha256:dfd617f69b3af15e1fad323e893c535ef022c9efb9528fb53ad6c8ec44741d5a
Copying blob sha256:b4aebd139799aa429f45564ceac662ba2bc66115fb8c0318cd3b2368ea7517e4
Copying config sha256:b960411dc937f9b4d9762349f5f77772d36dead003baa3bc01330abe8e1f38a6
Writing manifest to image destination
--> b960411dc937
[2/2] STEP 1/7: FROM debian:trixie-slim
Resolved "debian" as an alias (/etc/containers/registries.conf.d/000-shortnames.conf)
Trying to pull docker.io/library/debian:trixie-slim...
...
```
<details>

<summary>Expand for more output</summary>

```console
...
Getting image source signatures
Copying blob sha256:5b4d6ff92fc4e14e911b7753c954fac965d48c40fe1075758d284148ccace970
Copying config sha256:f283d70f878433b889e4b9252110fad858e0e0887df5bac91cd2ad4ccb2b3a2a
Writing manifest to image destination
[2/2] STEP 2/7: ENV DEBIAN_FRONTEND=noninteractive
--> 5808b4b9aad3
[2/2] STEP 3/7: RUN apt-get update && apt-get install -y python3.13 
Get:1 http://deb.debian.org/debian trixie InRelease [140 kB]
Get:2 http://deb.debian.org/debian trixie-updates InRelease [47.3 kB]
Get:3 http://deb.debian.org/debian-security trixie-security InRelease [43.4 kB]
Get:4 http://deb.debian.org/debian trixie/main amd64 Packages [9671 kB]
Get:5 http://deb.debian.org/debian trixie-updates/main amd64 Packages [5412 B]
Get:6 http://deb.debian.org/debian-security trixie-security/main amd64 Packages [192 kB]
Fetched 10.1 MB in 2s (4109 kB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
  ca-certificates libexpat1 libffi8 libgpm2 libncursesw6 libpython3.13-minimal
  libpython3.13-stdlib libreadline8t64 media-types netbase openssl
  python3.13-minimal readline-common
Suggested packages:
  gpm python3.13-venv python3.13-doc binutils binfmt-support readline-doc
The following NEW packages will be installed:
  ca-certificates libexpat1 libffi8 libgpm2 libncursesw6 libpython3.13-minimal
  libpython3.13-stdlib libreadline8t64 media-types netbase openssl python3.13
  python3.13-minimal readline-common
0 upgraded, 14 newly installed, 0 to remove and 0 not upgraded.
Need to get 8020 kB of archives.
After this operation, 27.1 MB of additional disk space will be used.
Get:1 http://deb.debian.org/debian trixie/main amd64 libexpat1 amd64 2.7.1-2 [108 kB]
Get:2 http://deb.debian.org/debian trixie/main amd64 libpython3.13-minimal amd64 3.13.5-2+deb13u2 [862 kB]
Get:3 http://deb.debian.org/debian trixie/main amd64 python3.13-minimal amd64 3.13.5-2+deb13u2 [2217 kB]
Get:4 http://deb.debian.org/debian trixie/main amd64 netbase all 6.5 [12.4 kB]
Get:5 http://deb.debian.org/debian trixie/main amd64 readline-common all 8.2-6 [69.4 kB]
Get:6 http://deb.debian.org/debian trixie/main amd64 openssl amd64 3.5.6-1~deb13u1 [1503 kB]
Get:7 http://deb.debian.org/debian trixie/main amd64 ca-certificates all 20250419 [162 kB]
Get:8 http://deb.debian.org/debian trixie/main amd64 media-types all 13.0.0 [29.3 kB]
Get:9 http://deb.debian.org/debian trixie/main amd64 libffi8 amd64 3.4.8-2 [24.1 kB]
Get:10 http://deb.debian.org/debian trixie/main amd64 libgpm2 amd64 1.20.7-11+b2 [14.4 kB]
Get:11 http://deb.debian.org/debian trixie/main amd64 libncursesw6 amd64 6.5+20250216-2 [135 kB]
Get:12 http://deb.debian.org/debian trixie/main amd64 libreadline8t64 amd64 8.2-6 [169 kB]
Get:13 http://deb.debian.org/debian trixie/main amd64 libpython3.13-stdlib amd64 3.13.5-2+deb13u2 [1958 kB]
Get:14 http://deb.debian.org/debian trixie/main amd64 python3.13 amd64 3.13.5-2+deb13u2 [757 kB]
Preconfiguring packages ...
Fetched 8020 kB in 1s (6819 kB/s)
Selecting previously unselected package libexpat1:amd64.
(Reading database ... 4936 files and directories currently installed.)
Preparing to unpack .../00-libexpat1_2.7.1-2_amd64.deb ...
Unpacking libexpat1:amd64 (2.7.1-2) ...
Selecting previously unselected package libpython3.13-minimal:amd64.
Preparing to unpack .../01-libpython3.13-minimal_3.13.5-2+deb13u2_amd64.deb ...
Unpacking libpython3.13-minimal:amd64 (3.13.5-2+deb13u2) ...
Selecting previously unselected package python3.13-minimal.
Preparing to unpack .../02-python3.13-minimal_3.13.5-2+deb13u2_amd64.deb ...
Unpacking python3.13-minimal (3.13.5-2+deb13u2) ...
Selecting previously unselected package netbase.
Preparing to unpack .../03-netbase_6.5_all.deb ...
Unpacking netbase (6.5) ...
Selecting previously unselected package readline-common.
Preparing to unpack .../04-readline-common_8.2-6_all.deb ...
Unpacking readline-common (8.2-6) ...
Selecting previously unselected package openssl.
Preparing to unpack .../05-openssl_3.5.6-1~deb13u1_amd64.deb ...
Unpacking openssl (3.5.6-1~deb13u1) ...
Selecting previously unselected package ca-certificates.
Preparing to unpack .../06-ca-certificates_20250419_all.deb ...
Unpacking ca-certificates (20250419) ...
Selecting previously unselected package media-types.
Preparing to unpack .../07-media-types_13.0.0_all.deb ...
Unpacking media-types (13.0.0) ...
Selecting previously unselected package libffi8:amd64.
Preparing to unpack .../08-libffi8_3.4.8-2_amd64.deb ...
Unpacking libffi8:amd64 (3.4.8-2) ...
Selecting previously unselected package libgpm2:amd64.
Preparing to unpack .../09-libgpm2_1.20.7-11+b2_amd64.deb ...
Unpacking libgpm2:amd64 (1.20.7-11+b2) ...
Selecting previously unselected package libncursesw6:amd64.
Preparing to unpack .../10-libncursesw6_6.5+20250216-2_amd64.deb ...
Unpacking libncursesw6:amd64 (6.5+20250216-2) ...
Selecting previously unselected package libreadline8t64:amd64.
Preparing to unpack .../11-libreadline8t64_8.2-6_amd64.deb ...
Adding 'diversion of /lib/x86_64-linux-gnu/libhistory.so.8 to /lib/x86_64-linux-gnu/libhistory.so.8.usr-is-merged by libreadline8t64'
Adding 'diversion of /lib/x86_64-linux-gnu/libhistory.so.8.2 to /lib/x86_64-linux-gnu/libhistory.so.8.2.usr-is-merged by libreadline8t64'
Adding 'diversion of /lib/x86_64-linux-gnu/libreadline.so.8 to /lib/x86_64-linux-gnu/libreadline.so.8.usr-is-merged by libreadline8t64'
Adding 'diversion of /lib/x86_64-linux-gnu/libreadline.so.8.2 to /lib/x86_64-linux-gnu/libreadline.so.8.2.usr-is-merged by libreadline8t64'
Unpacking libreadline8t64:amd64 (8.2-6) ...
Selecting previously unselected package libpython3.13-stdlib:amd64.
Preparing to unpack .../12-libpython3.13-stdlib_3.13.5-2+deb13u2_amd64.deb ...
Unpacking libpython3.13-stdlib:amd64 (3.13.5-2+deb13u2) ...
Selecting previously unselected package python3.13.
Preparing to unpack .../13-python3.13_3.13.5-2+deb13u2_amd64.deb ...
Unpacking python3.13 (3.13.5-2+deb13u2) ...
Setting up libexpat1:amd64 (2.7.1-2) ...
Setting up media-types (13.0.0) ...
Setting up libgpm2:amd64 (1.20.7-11+b2) ...
Setting up libpython3.13-minimal:amd64 (3.13.5-2+deb13u2) ...
Setting up libncursesw6:amd64 (6.5+20250216-2) ...
Setting up libffi8:amd64 (3.4.8-2) ...
Setting up python3.13-minimal (3.13.5-2+deb13u2) ...
Setting up netbase (6.5) ...
Setting up openssl (3.5.6-1~deb13u1) ...
Setting up readline-common (8.2-6) ...
Setting up ca-certificates (20250419) ...
Updating certificates in /etc/ssl/certs...
150 added, 0 removed; done.
Setting up libreadline8t64:amd64 (8.2-6) ...
Setting up libpython3.13-stdlib:amd64 (3.13.5-2+deb13u2) ...
Setting up python3.13 (3.13.5-2+deb13u2) ...
Processing triggers for libc-bin (2.41-12+deb13u3) ...
Processing triggers for ca-certificates (20250419) ...
Updating certificates in /etc/ssl/certs...
0 added, 0 removed; done.
Running hooks in /etc/ca-certificates/update.d...
done.
--> 4f123f8d89fe
[2/2] STEP 4/7: RUN ln -s /usr/bin/python3.13 /usr/bin/python
--> 6dd8a6c94600
[2/2] STEP 5/7: COPY --from=uv /uv /usr/local/bin/uv
--> b907eed1ae8b
[2/2] STEP 6/7: WORKDIR /workspace
--> 55b854bc8dcd
[2/2] STEP 7/7: CMD ["/bin/bash"]
[2/2] COMMIT test_trixie
--> 7bab3cfc2aa3
...
```
</details>

```console
...
Successfully tagged localhost/test_trixie:latest
7bab3cfc2aa34bf43d9a63ccb8428a859c9f64a807186a4262b17bc5ffe0b4eb
```

Then, I'll run the container with the following flags (see the [Podman run docs](https://docs.podman.io/en/latest/markdown/podman-run.1.html) for details):
- `-i`: Interactive
    - "When set to true, make `stdin` available to the contained process. If false, the `stdin` of the contained process is empty and immediately closed."
- `-t`: TTY
    - "Allocate a pseudo-TTY. The default is false. When set to true, Podman allocates a pseudo-tty and attach to the standard input of the container. This can be used, for example, to run a throwaway interactive shell."
- `--rm`: Remove upon exit
    - "Automatically remove the container and any anonymous unnamed volume associated with the container when it exits. The default is false."
- `--name`: Container name
    - "Assign a name to the container." This can be completely different from the name of the image it is built from.
```console
Grey@Audron:seaicecp$ podman run -it --rm --name container_name test_trixie
root@c6dc2f68fd76:/workspace# 
```
While this container is running, I can hit the refresh button in the Pod Manager sidebar to see that there is a new container named `container_name`.
I can also verify that Python and `uv` are installed inside the container.
```console
root@c6dc2f68fd76:/workspace# python
Python 3.13.5 (main, May  5 2026, 21:05:52) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
root@c6dc2f68fd76:/workspace# uv --version
uv 0.11.17 (x86_64-unknown-linux-musl)
root@c6dc2f68fd76:/workspace#
```
When I am done, I can exit the container.
```console
root@c6dc2f68fd76:/workspace# exit
exit
Grey@Audron:seaicecp$ 
```
Upon exiting the container, I can refresh the Pod Manager sidebar again to see that the container removed itself upon exit because of the `--rm` flag.
This is important to keep from building up a large number of idle containers when starting a particular image many times.

With this working, the next step is to build out the `Containerfile` to set up the development environment with all the necessary packages, tools, and data access.

---

<a id='podman_containerfile'></a>
[back to top](#top)

### The `Containerfile`

Below is the current `Containerfile` used to build the image for this project.

```{literalinclude} ../../.devcontainer/Containerfile
:language: dockerfile
```

Note that this is meant to be executed via the [`start_container.sh` script](#podman_start_container).
However, if testing a new build, it can be useful to pipe the output of `podman build` to a log file using `tee`.
```console
Grey@Audron:seaicecp$ podman build -f .devcontainer/Containerfile -t <image_name> . | tee .devcontainer/<log_file_name>.log
```

I'll explain each section of the `Containerfile` in detail below.

<a id='podman_containerfile_pin_versions'></a>
[back to top](#top)

#### Pinning the versions of `uv` and `trixie-slim`

For reproducibility purposes, I decided to pin the exact versions of `uv` and `trixie-slim` that my container uses. 
After [Building a simple container](#podman_simple_container), I now see the following images in the Pod Manger sidebar:
- `ghcr.io/astral-sh/uv:latest`
- `docker.io/library/debian:trixie-slim`

I can get the exact hashes of the versions of `uv` and `trixie-slim` from their manifests.
```console
Grey@Audron:seaicecp$ podman image inspect debian:trixie-slim --format '{{.Digest}}'
sha256:e18da95f66066b7c5fa31491b524e83121271eca59a3d140f4906c8d0a090367
Grey@Audron:seaicecp$ podman image inspect ghcr.io/astral-sh/uv --format '{{.Digest}}'
sha256:5cbec7ab7753a6c763c6dda6a38f085c8c585ec9f53cfb4e7368b79ca30bc881
```

<a id='podman_containerfile_env_vars'></a>
[back to top](#top)

#### Defining environment variables

The `Containerfile` defines a few environment variables to facilitate building the image.
- `DEBIAN_FRONTEND=noninteractive`
    - According to the askUbuntu post [DEBIAN_FRONTEND environment variable](https://askubuntu.com/questions/972516/debian-frontend-environment-variable), this prevents installations from getting stuck on interactive processes, such as when the user is asked to confirm or select something.
- `ENV UV_PROJECT_ENVIRONMENT=/workspace/.cvenv`
    - According to the Python Developer Tooling Handbook on [How to customize uv's virtual environment location](https://pydevtools.com/handbook/how-to/how-to-customize-uvs-virtual-environment-location/), this renames the default directory for the `uv` virtual environment from `.venv` to `.cvenv` to avoid conflicts with using the environment inside vs. outside the container.
    - Note that the use of the directory `/workspace` is [detailed below](#podman_containerfile_misc_prep).
- `ENV UV_LINK_MODE=copy`
    - According to the Python Developer Tooling Handbook on [How to use `uv` in a Dockerfile](https://pydevtools.com/handbook/how-to/how-to-use-uv-in-a-dockerfile/), this "tells uv to copy files instead of hard-linking them. When using Docker cache mounts, the cache and the target directory live on separate filesystems, so uv falls back to copying anyway. Setting this explicitly avoids the warning message."

<a id='podman_containerfile_apt-get'></a>
[back to top](#top)

#### Installing system and scientific dependencies

The next block in the `Containerfile` uses `apt-get` to install the necessary system-level dependencies for the project. 
The flags used here are:
- `-y`: Assume yes
    - From the [Linux manual page for `apt-get`](https://linux.die.net/man/8/apt-get), "Automatic yes to prompts. Assume 'yes' as answer to all prompts and run non-interactively. If an undesirable situation, such as changing a held package or removing an essential package, occurs then `apt-get` will abort."
- `--no-install-recommends`: 
    - According to the askUbuntu post [How to not install recommended and suggested packages?](https://askubuntu.com/questions/179060/how-to-not-install-recommended-and-suggested-packages), this flag prevents `apt-get` from automatically installing recommended packages, keeping the container's stack to a minimum, installing only what is required.

The packages installed in this block are:
- `ca-certificates`
- `curl`
- `git`
    - For version control.
- `build-essential`
- `pkg-config`
- `unzip`
- `libnetcdf-dev`
    - For working with netCDF files.
- `netcdf-bin`
    - For working with netCDF files.
- `libhdf5-dev`
    - For working with netCDF files.
- `libcurl4-openssl-dev`
    - For establishing Secure Sockets Layer (SSL) for internet connections.
- `libssl-dev`
    - For establishing Secure Sockets Layer (SSL) for internet connections.
- `cdo`
    - [Climate Data Operators](https://code.mpimet.mpg.de/projects/cdo)
- `nco`
    - [netCDF Operators](https://nco.sourceforge.net/nco.html)
- `python3.13`
    - The version of Python used in this project.
- `python3.13-venv`
    - For using Python in a virtual environment.
- `python3-pip`
    - For installing packages that `uv` cannot handle natively.

<a id='podman_containerfile_misc_prep'></a>
[back to top](#top)

#### Preparing Python, `uv`, and working directory

- `RUN ln -s /usr/bin/python3.13 /usr/bin/python`
    - This command creates a symlink such that using the command `python` calls Python 3.13.
    - This removes the need to specify the version of Python to use every time.
- `COPY --from=uv /uv /usr/local/bin/uv`
    - From [Using `uv` in Docker](https://docs.astral.sh/uv/guides/integration/docker/), this command copies `uv` from where it was downloaded into the `usr` directory for ease of use.
- `WORKDIR /workspace`
    - This sets the working directory to be named `/workspace`.
    - The choice of the name is arbitrary, however sets a specific file path that can be expected by other parts of the project.
    - This essentially renames the root of the project directory on your computer (`seaicecp`) to be `/workspace` inside the container. 
- The next three commands set up dependency files for the virtual environment.
    - `COPY pyproject.toml uv.lock ./`
    - `COPY README.md ./`
    - `COPY src ./src`

<a id='podman_containerfile_uv_jupyter'></a>
[back to top](#top)

#### `uv` dependencies and Jupyter kernel

The next block in the `Containerfile` is:
```dockerfile
...
# Install dependencies via `uv` and start a kernel for Jupyter notebooks
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
 && uv run python -m ipykernel install --sys-prefix --name python3 --display-name "seaicecp (container)"
...
```

This installs and/or updates all the dependencies defined in the `pyproject.toml` file using `uv sync`.
Specifying `--mount=type=cache,target=/root/.cache/uv` will cache the packages with `uv`, making subsequent builds much faster.
Then, it starts a kernel for using the Python virtual environment in Jupyter notebooks. 

<a id='podman_containerfile_natural_earth'></a>
[back to top](#top)

#### Download commonly used Natural Earth shapefiles

When making maps, it is often useful to plot coastlines or other shapes to give context. 
A common way of doing this in Python is from Natural Earth shape files.
There are a couple of common files that the next block of the `Containerfile` downloads so that it won't need to be downloaded the first time a plot is made that requires them.
```dockerfile
...
# Trigger downloads of commonly used Natural Earth datasets
RUN /workspace/.cvenv/bin/python - <<'EOF'
import cartopy.io.shapereader as shp
shp.natural_earth(resolution='110m', category='physical', name='coastline')
EOF
...
```
If this is not present in the image, the following warning occurs when making a plot that requires downloading shape files.
```console
/workspace/.venv/lib/python3.13/site-packages/cartopy/io/__init__.py:242: DownloadWarning: Downloading: https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip
  warnings.warn(f'Downloading: {url}', DownloadWarning)
```

<a id='podman_containerfile_esgpull'></a>
[back to top](#top)

#### Set up `esgpull` install

This project uses the `esgpull` tool to download HighResMIP data files.
This next block sets up an install of `esgpull` on an external volume.
```dockerfile
...
# Set up the `esgpull` install
COPY .devcontainer/esgpull_entrypoint.sh /esgpull_entrypoint.sh
RUN chmod +x /esgpull_entrypoint.sh
ENTRYPOINT ["/esgpull_entrypoint.sh"]
...
```
This uses the separate script included with this project at `.devcontainer/esgpull_entrypoint.sh` which is shown below.
```{literalinclude} ../../.devcontainer/esgpull_entrypoint.sh
:language: bash
```

The `.devcontainer/esgpull_entrypoint.sh` script assumes that the directory in which the data on the external volume is stored has been defined as `/seaicecp_data`, something which is set when executing the `podman run` command.

<a id='podman_containerfile_jupyter_server'></a>
[back to top](#top)

#### Set up the Jupyter server

The last block of the `Containerfile` exposes port 8888 of the container and sets up the Jupyter server to run on that port with no password or identity token.

```dockerfile
...
# Expose the port for the Jupyter server
EXPOSE 8888

CMD ["bash", "-lc", "exec uv run jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --IdentityProvider.token='' \
    --ServerApp.password=''"]
```

Note that port 8888 in the container will be set to connect to a different port (8889) on the host machine later.

---

<a id='podman_start_container'></a>
[back to top](#top)

### The `start_container` script

[The `Containerfile`](#podman_containerfile) defines how the image for this project should be built.
I created a script called `start_container.sh` which ultimately starts the container from that image, but first checkes to make sure the Podman virtual machine is running and whether the image exists already.
The script is shown below:

```{literalinclude} ../../start_container.sh
:language: bash
```

I'll explain each section in detail below.

<a id='podman_start_container_pipefail'></a>
[back to top](#top)

#### Set the script to fail on common errors

The first line is `set -euo pipefail`. 
The GitHub Gist by `akrasic` called [`bash_strict_mode`](https://gist.github.com/akrasic/380bda362e0420be08709152c91ca1f9) explains that the `set` command is used to cause a script to fail very explicitly when encountering errors. 
This can be helpful to track down where exactly the bugs are, especially if the script calls other scripts. 

<a id='podman_start_container_machine_status'></a>
[back to top](#top)

#### Ensure the virtual machine is running

The next block checks the status of the virtual machine, which is required for running on macOS.
First, it checks whether the machine has been initialized.

```bash
...
# ---- Ensure podman machine is running (macOS) ----
if ! podman machine inspect >/dev/null 2>&1; then
  echo "No podman machine found. Initializing..."
  podman machine init
fi
...
```
Then, it gets the state of the machine to see whether it has already been started.
```bash
...
MACHINE_STATE=$(podman machine inspect --format '{{.State}}')

if [[ "$MACHINE_STATE" != "running" ]]; then
  echo "Starting podman machine..."
  podman machine start
fi
...
```

This block allows you to re-run the `start_container.sh` script even if you already have the Podman machine running.
This is useful when testing the code in a way which requires restarting the container frequently.

<a id='podman_start_container_params'></a>
[back to top](#top)

#### Set the parameters

Next, the scripts sets the following parameters.

- `IMAGE="seaicecp_7"`
    - This will be the name of the image that is built. 
    - If an image with this name already exists, a new one will not be built.
    - If you want to try a new build, change this parameter.
- `CONTAINER_NAME="sicp_cont"`
    - This is the name that the container will have when it is running.
    - If you want to have multiple containers running at the same time, you might need to change this.
- `WORKDIR="/workspace"`
    - This defines the name of the working directory for the container.
    - This must be the same name used in the `Containerfile`.

<a id='podman_start_container_cleanup'></a>
[back to top](#top)

#### Check existing containers and images

The next two blocks clean up any existing images and builds the image, if necessary.
```bash
...
# ---- Cleanup old container if it exists ----
podman rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

# ---- Ensure image exists ----
if ! podman image exists "$IMAGE"; then
  echo "Image $IMAGE not found. Building from '.devcontainer/Containerfile'..."
  podman build -f .devcontainer/Containerfile -t "$IMAGE" . | tee .devcontainer/build_container_log.txt
fi
...
```

The `|| true` in the first command ensures that it executes successfully, even when there is no old container to clean up. 
In the second part, the image building step will be skipped if an image with the given name already exists.

<a id='podman_start_container_external_vol'></a>
[back to top](#top)

#### Set up access to external volumes

The next block sets up access to data on an external volume.
The value of `SICP_DATA_DIR` should be changed to match the absolute file path of your external hard drive where `esgpull` will store the HighResMIP data.

```bash
...
# ---- Setup external hard drive access ----
export SICP_DATA_DIR=/Volumes/BERGY_BITS/seaicecp_data/
SICP_DATA_DIR="${SICP_DATA_DIR:-}"

if [[ -n "$SICP_DATA_DIR" ]]; then
  if [[ ! -d "$SICP_DATA_DIR" ]]; then
    echo "ERROR: SICP_DATA_DIR does not exist: $SICP_DATA_DIR"
    exit 1
  fi
fi
...
```
If you need to change the external volume setup, you will need to restart the Podman machine, not just the container, to see whether the change worked.
```console
Grey@Audron:seaicecp$ podman machine stop
Machine "podman-machine-default" stopped successfully
Grey@Audron:seaicecp$ podman machine rm
The following files will be deleted:


/Users/Grey/.config/containers/podman/machine/applehv/podman-machine-default.json
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default.sock
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default-gvproxy.sock
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default-api.sock
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default.log
Are you sure you want to continue? [y/N] y
```

<a id='podman_start_container_list_vol'></a>
[back to top](#top)

#### Create the list of volumes

The next block creates the list of arguments to be used to define the volumes.
This should include the working directory and the external volume.
```bash
...
# ---- Build volume args ----
VOLUMES=(-v "$(pwd)":"$WORKDIR")

if [[ -n "$SICP_DATA_DIR" ]]; then
  VOLUMES+=(-v "$SICP_DATA_DIR:/seaicecp_data")
fi
...
```

<a id='podman_start_container_run'></a>
[back to top](#top)

#### Run the container

Finally, the script starts the container with the `podman run` command.
```bash
...
# ---- Run container (Jupyter starts automatically from CMD) ----
podman run -it --rm \
  --name "$CONTAINER_NAME" \
  -p 8889:8888 \
  "${VOLUMES[@]}" \
  -w "$WORKDIR" \
  "$IMAGE"
```
The arguments of the command are, similar to [Building a simple container](#podman_simple_container) (see the [Podman run docs](https://docs.podman.io/en/latest/markdown/podman-run.1.html) for details):
- `-i`: Interactive
    - "When set to true, make `stdin` available to the contained process. If false, the `stdin` of the contained process is empty and immediately closed."
- `-t`: TTY
    - "Allocate a pseudo-TTY. The default is false. When set to true, Podman allocates a pseudo-tty and attach to the standard input of the container. This can be used, for example, to run a throwaway interactive shell."
- `--rm`: Remove upon exit
    - "Automatically remove the container and any anonymous unnamed volume associated with the container when it exits. The default is false."
- `--name`: Container name
    - "Assign a name to the container." This can be completely different from the name of the image it is built from.
- `-p`: Publish (Ports)
    - "Publish a container’s port, or range of ports, to the host. Both hostPort and containerPort can be specified as a range of ports. When specifying ranges for both, the number of container ports in the range must match the number of host ports in the range."
    - This is set here as `8889:8888` to specify that the host system (my laptop) will use port 8889 (to avoid conflicts with existing Jupyter servers) to connect to the container's port 8888 where it's Jupyter server is running.
- `"${VOLUMES[@]}"`: List of volumes
    - The list of directories (`/workspace` and the external volume) that the container should have access to.
- `-w`: Working directory
    - "Working directory inside the container. The default working directory for running binaries within a container is the root directory (`/`). The image developer can set a different default with the `WORKDIR` instruction. The operator can override the working directory by using the `-w` option."
- `"$IMAGE"`
    - The name of the image to use for this container.


<a id='venv'></a>
[back to top](#top)

## Virtual environment and packages

<a id='venv_activate'></a>
[back to top](#top)

### Activating the virtual environment

When initializing the project, `uv` automatically creates a virtual environment in `.venv/`.
I can easily activate it by sourcing that directory.
```console
seaicecp$ source .venv/bin/activate
(seaicecp) seaicecp$ 
```

<a id='venv_dependencies'></a>
[back to top](#top)

### Adding package dependencies

Using `uv` to add dependencies works similarly to `poetry` as described in [3.6. Adding dependencies to your package](https://py-pkgs.org/03-how-to-package-a-python). 
See `uv` docs for [The project environment](https://docs.astral.sh/uv/concepts/projects/layout/#the-project-environment). 

```console
Grey@Audron:seaicecp$ uv add geoviews
Using CPython 3.14.1
Creating virtual environment at: .venv
Resolved 47 packages in 1.35s
      Built cartopy==0.25.0
Prepared 44 packages in 36.06s
Installed 44 packages in 488ms
 + bleach==6.3.0
 + bokeh==3.9.0
 + cartopy==0.25.0
 + certifi==2026.2.25
 + charset-normalizer==3.4.7
 + colorcet==3.1.0
 + contourpy==1.3.3
 + cycler==0.12.1
 + fonttools==4.62.1
 + geoviews==1.15.1
 + holoviews==1.22.1
 + idna==3.11
 + jinja2==3.1.6
 + kiwisolver==1.5.0
 + linkify-it-py==2.1.0
 + markdown==3.10.2
 + markdown-it-py==4.0.0
 + markupsafe==3.0.3
 + matplotlib==3.10.8
 + mdit-py-plugins==0.5.0
 + mdurl==0.1.2
 + narwhals==2.19.0
 + numpy==2.4.4
 + packaging==26.0
 + pandas==3.0.2
 + panel==1.8.10
 + param==2.3.3
 + pillow==12.2.0
 + pyparsing==3.3.2
 + pyproj==3.7.2
 + pyshp==3.0.3
 + python-dateutil==2.9.0.post0
 + pyviz-comms==3.0.6
 + pyyaml==6.0.3
 + requests==2.33.1
 + shapely==2.1.2
 + six==1.17.0
 + tornado==6.5.5
 + tqdm==4.67.3
 + typing-extensions==4.15.0
 + uc-micro-py==2.0.0
 + urllib3==2.6.3
 + webencodings==0.5.1
 + xyzservices==2026.3.0
```

In running that command, I got a pop-up in VSCodium asking: "We noticed a new environment has been created. Do you want to select it for the workspace folder?" I clicked "Yes"

I notice from the list above that `xarray` is not installed. I'll go ahead and add that as well.

```console
Grey@Audron:seaicecp$ uv add xarray
Resolved 48 packages in 343ms
Prepared 1 package in 318ms
Installed 1 package in 11ms
 + xarray==2026.4.0
```

In order to load data from NetCDF files into an `xarray` dataset, I also need to add the `netcdf4` package.

```console
Grey@Audron:seaicecp$ source .venv/bin/activate
(seaicecp) Grey@Audron:seaicecp$ uv add netcdf4
Resolved 78 packages in 716ms
Prepared 2 packages in 3.74s
Installed 2 packages in 13ms
 + cftime==1.6.5
 + netcdf4==1.7.4
```

<a id='esgpull'></a>
[back to top](#top)

### Adding `esgpull`

I want to try downloading more datasets to see whether they are all like this. I found the project [esgpull](https://esgf.github.io/esgf-download/quickstart/) which offers a command line interface for searching and downloading, which I think would be nice as searching on the [ESGF Federated Nodes](https://esgf-node.ornl.gov/search) is a bit tedious with the GUI. 

I'll add `esgpull` as a dependency in my project following the [installation guide](https://esgf.github.io/esgf-download/installation/) which has an example using `uv` which is great.

I came back to this later as I noticed that this didn't actually add `esgpull` to the `.toml` file.
Perhaps I should try installing it with simply `uv add esgpull`?
Would that perhaps mess up the installation I already have? Unclear. 
I could try using the flag `--dry-run` and see what would happen.

```console
(seaicecp) Grey@Audron:seaicecp$ uv tool install esgpull
Resolved 43 packages in 184ms
Prepared 1 package in 142ms
Installed 43 packages in 172ms
 + aiofiles==25.1.0
 + aiostream==0.7.1
 + alembic==1.18.4
 + annotated-types==0.7.0
 + anyio==4.13.0
 + attrs==26.1.0
 + cattrs==26.1.0
 + certifi==2026.2.25
 + cffi==2.0.0
 + click==8.3.2
 + click-params==0.5.0
 + cryptography==46.0.7
 + deprecated==1.3.1
 + esgpull==0.9.6
 + greenlet==3.4.0
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + idna==3.11
 + mako==1.3.11
 + markdown-it-py==4.0.0
 + markupsafe==3.0.3
 + mdurl==0.1.2
 + nest-asyncio==1.6.0
 + packaging==26.1
 + platformdirs==4.9.6
 + pycparser==3.0
 + pydantic==2.13.0
 + pydantic-core==2.46.0
 + pydantic-settings==2.13.1
 + pygments==2.20.0
 + pyopenssl==26.0.0
 + pyparsing==3.3.2
 + python-dotenv==1.2.2
 + pyyaml==6.0.3
 + rich==15.0.0
 + setuptools==82.0.1
 + sqlalchemy==2.0.49
 + tomlkit==0.14.0
 + typing-extensions==4.15.0
 + typing-inspection==0.4.2
 + validators==0.22.0
 + wrapt==2.1.2
Installed 1 executable: esgpull
```

Note: I needed to start a new terminal before the following would work:
```console
(seaicecp) Grey@Audron:seaicecp$ esgpull --version
esgpull, version 0.9.6
```

Then, I needed to do the second step of installation to allow it to write data:
```console
(seaicecp) Grey@Audron:seaicecp$ esgpull self install
──────────────────────────────────────────────────── esgpull installation ────────────────────────────────────────────────────
Install location (/Users/Grey/.esgpull): .esgpull
Name (optional): seaicecp
Creating install directory and files at /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull
Install config added to /Users/Grey/Library/Application Support/esgpull/installs.json
```

I checked the configuration because the "Server error '500 500' for url 'https://esgf-node.ipsl.upmc.fr/..." got me suspicious as to why it was selected a French web domain:
```console
(seaicecp) Grey@Audron:seaicecp$ esgpull config
──────────────── /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/config.toml ────────────────
[paths]
data = "/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/data"
db = "/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/db"
log = "/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/log"
tmp = "/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/tmp"
plugins = "/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/plugins"

[credentials]
filename = "credentials.toml"

[cli]
page_size = 20

[db]
filename = "esgpull.db"

[download]
chunk_size = 67108864
http_timeout = 20
max_concurrent = 5
disable_ssl = false
disable_checksum = false
show_filename = false

[api]
index_node = "esgf-node.ipsl.upmc.fr"
http_timeout = 20
max_concurrent = 5
page_limit = 50
default_query_id = ""
use_custom_distribution_algorithm = false

[api.default_options]
distrib = "true"
latest = "true"
replica = "none"
retracted = "false"

[plugins]
enabled = false
```

So, that was the issue. I changed the index node to be the one recommended for the USA region:

```console
(seaicecp) Grey@Audron:seaicecp$ esgpull config api.index_node esgf-node.ornl.gov/esgf-1-5-bridge
[api]
index_node = "esgf-node.ornl.gov/esgf-1-5-bridge"

👍 New config file created at /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull/config.toml.
```

Then, I was finally able to search:
```console
(seaicecp) Grey@Audron:seaicecp$ esgpull search
Found 14423347 datasets.
 id │                               dataset                               │ #  │   size    
════╪═════════════════════════════════════════════════════════════════════╪════╪═══════════
  0 │ cmip5.output.CCCma.CanCM4.decadal1967.mon.land.r7i1p1.v20130331     │ 11 │  56.4 MiB 
  1 │ cmip5.output.CCCma.CanCM4.decadal1967.mon.landIce.r5i1p1.v20130331  │  6 │  22.6 MiB 
  2 │ cmip5.output.CCCma.CanCM4.decadal1982.mon.landIce.r2i1p1.v20130331  │  6 │  22.6 MiB 
  3 │ cmip5.output.CCCma.CanCM4.decadal1982.mon.landIce.r7i1p1.v20130331  │  6 │  22.6 MiB 
  4 │ cmip5.output.CCCma.CanCM4.decadal1982.mon.ocean.r5i1p1.v20130331    │ 32 │   6.6 GiB 
  5 │ cmip5.output.CCCma.CanCM4.decadal1983.day.atmos.r4i1p1.v20130331    │ 23 │   2.6 GiB 
  6 │ cmip5.output.CCCma.CanCM4.decadal1983.day.landIce.r8i1p1.v20130331  │  2 │ 228.3 MiB 
  7 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.atmos.r2i1p1.v20130331    │ 47 │   1.1 GiB 
  8 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.land.r5i1p1.v20130331     │ 11 │  56.4 MiB 
  9 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.landIce.r2i1p1.v20130331  │  6 │  22.6 MiB 
 10 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.ocean.r8i1p1.v20130331    │ 32 │   6.6 GiB 
 11 │ cmip5.output.CCCma.CanCM4.decadal1984.day.atmos.r2i1p1.v20130331    │ 23 │   2.6 GiB 
 12 │ cmip5.output.CCCma.CanCM4.decadal1984.day.landIce.r10i1p1.v20130331 │  2 │ 228.3 MiB 
 13 │ cmip5.output.CCCma.CanCM4.decadal1984.day.seaIce.r3i1p1.v20130331   │  4 │ 456.6 MiB 
 14 │ cmip5.output.CCCma.CanCM4.decadal1980.mon.ocean.r7i1p1.v20130331    │ 96 │  19.8 GiB 
 15 │ cmip5.output.CCCma.CanCM4.decadal1980.mon.ocean.r8i1p1.v20130331    │ 96 │  19.8 GiB 
 16 │ cmip5.output.CCCma.CanCM4.decadal1990.day.atmos.r10i2p1.v20130331   │ 23 │   2.6 GiB 
 17 │ cmip5.output.CCCma.CanCM4.decadal1990.day.atmos.r4i1p1.v20130331    │ 23 │   2.6 GiB 
 18 │ cmip5.output.CCCma.CanCM4.decadal1990.day.atmos.r6i1p1.v20130331    │ 23 │   2.6 GiB 
 19 │ cmip5.output.CCCma.CanCM4.decadal1990.day.land.r5i2p1.v20130331     │  3 │ 342.5 MiB
```

[esgpull download guide](https://esgf.github.io/esgf-download/download/)

<a id='esgpull_ext_HD'></a>
[back to top](#top)

#### Adding `esgpull` install on an external drive

The location chosen for the install is where the data files will be stored. 
My computer's internal hard drive is not large enough to store all the data I will be working with.
To avoid filling up my hard drive, I created a separate `esgpull` install on my external disk. 

First, I confirmed the location of the install I had already done.
```console
Grey@Audron:seaicecp$ esgpull self choose
Install locations                                                                                
 *  /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull  seaicecp
```

I could not figure out how to input absolute file paths when creating a new `esgpull` install, so I first navigated my terminal to the location in which I wanted it to be.
```console
Grey@Audron:seaicecp$ cd /Volumes/BERGY_BITS/seaicecp_data/
```

Then, I created a new install, giving it a memorable name
```console
Grey@Audron:seaicecp_data$ esgpull self install
──────────────────────────────────────────── esgpull installation ────────────────────────────────────────────
Install location (/Users/Grey/.esgpull): .esgpull
Name (optional): bergybits
Creating install directory and files at /Volumes/BERGY_BITS/seaicecp_data/.esgpull
Install config added to /Users/Grey/Library/Application Support/esgpull/installs.json
```

Now, I can navigate back to the home directory and check which install I have chosen currently.
```console
Grey@Audron:seaicecp_data$ cd ~/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/
Grey@Audron:seaicecp$ esgpull self choose
Install locations                                                                               
    /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull  seaicecp  
 *  /Volumes/BERGY_BITS/seaicecp_data/.esgpull 
```

I can confirm what data I've downloaded to each install by using the `show` command.
```console
Grey@Audron:seaicecp$ esgpull self choose -n bergybits
Grey@Audron:seaicecp$ esgpull self choose
Install locations                                                                               
    /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull  seaicecp  
 *  /Volumes/BERGY_BITS/seaicecp_data/.esgpull                                        bergybits 
Grey@Audron:seaicecp$ esgpull show
Grey@Audron:seaicecp$ esgpull self choose -n seaicecp
Grey@Audron:seaicecp$ esgpull self choose
Install locations                                                                               
 *  /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/.esgpull  seaicecp  
    /Volumes/BERGY_BITS/seaicecp_data/.esgpull                                        bergybits 
Grey@Audron:seaicecp$ esgpull show
<1a5a3a>
│ added    2026-04-14T23:07:27Z
│ updated  2026-04-14T23:11:11Z
└── distrib:       True               
    latest:        True               
    replica:       None               
    retracted:     False              
    activity_id:   HighResMIP         
    experiment_id: hist-1950          
    project:       CMIP6              
    source_id:     CESM1-CAM5-SE-HR   
    variable_id:   areacello          
    files:         1 / 1              
    datasets:      1 / 1              
    size:          63.1 MiB / 63.1 MiB
<b1c448>
│ added    2026-04-15T14:44:20Z
│ updated  2026-04-15T14:45:09Z
└── distrib:       True                 
    latest:        True                 
    replica:       None                 
    retracted:     False                
    activity_id:   HighResMIP           
    experiment_id: hist-1950            
    project:       CMIP6                
    variable_id:   areacello            
    files:         7 / 7                
    datasets:      7 / 7                
    size:          419.4 MiB / 419.4 MiB
```

I tried a search:
```console
Grey@Audron:seaicecp$ bash esgpull_searches/HRMIP_hist_areacello.sh 
[2026-04-17 13:58:13]  ERROR     root

  + Exception Group Traceback (most recent call last):
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/tui.py", line 191, in logging
  |     yield
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/cli/search.py", line 102, in search
  |     esg.context.probe()
  |     ~~~~~~~~~~~~~~~~~^^
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 815, in probe
  |     _ = self.hits(
  |         Query(),
  |         file=True,
  |         index_node=index_node or self.config.api.index_node,
  |     )
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 667, in hits
  |     return self._sync(self._hits(*results))
  |            ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 642, in _sync
  |     return sync(self._with_client(coro))
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/utils.py", line 17, in sync
  |     result = asyncio.run(coro)
  |   File "/Users/Grey/.local/share/uv/python/cpython-3.14.1-macos-x86_64-none/lib/python3.14/asyncio/runners.py", line 204, in run
  |     return runner.run(main)
  |            ~~~~~~~~~~^^^^^^
  |   File "/Users/Grey/.local/share/uv/python/cpython-3.14.1-macos-x86_64-none/lib/python3.14/asyncio/runners.py", line 127, in run
  |     return self._loop.run_until_complete(task)
  |            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  |   File "/Users/Grey/.local/share/uv/python/cpython-3.14.1-macos-x86_64-none/lib/python3.14/asyncio/base_events.py", line 719, in run_until_complete
  |     return future.result()
  |            ~~~~~~~~~~~~~^^
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 631, in _with_client
  |     return await coro
  |            ^^^^^^^^^^
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 551, in _hits
  |     async for result in self._fetch(*results):
  |     ...<4 lines>...
  |             hits.append(0)
  |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 547, in _fetch
  |     raise group
  | ExceptionGroup: fetch (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/esgpull/context.py", line 518, in _fetch_one
    |     resp.raise_for_status()
    |     ~~~~~~~~~~~~~~~~~~~~~^^
    |   File "/Users/Grey/.local/share/uv/tools/esgpull/lib/python3.14/site-packages/httpx/_models.py", line 829, in raise_for_status
    |     raise HTTPStatusError(message, request=request, response=self)
    | httpx.HTTPStatusError: Server error '500 500' for url 'https://esgf-node.ipsl.upmc.fr/esg-search/search?type=File&offset=0&limit=0&format=application%2Fsolr%2Bjson&fields=instance_id&distrib=true&latest=true&retracted=false'
    | For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
    +------------------------------------
ExceptionGroup: fetch (1 sub-exception)
See /Volumes/BERGY_BITS/seaicecp_data/.esgpull/log/esgpull-search-2026-04-17_17-58-12.log for error log.
Aborted!
```

I took a look at the config:
```console
Grey@Audron:seaicecp$ esgpull config
─────────────────────────── /Volumes/BERGY_BITS/seaicecp_data/.esgpull/config.toml ───────────────────────────
[paths]
data = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/data"
db = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/db"
log = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/log"
tmp = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/tmp"
plugins = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/plugins"

[credentials]
filename = "credentials.toml"

[cli]
page_size = 20

[db]
filename = "esgpull.db"

[download]
chunk_size = 67108864
http_timeout = 20
max_concurrent = 5
disable_ssl = false
disable_checksum = false
show_filename = false

[api]
index_node = "esgf-node.ipsl.upmc.fr"
http_timeout = 20
max_concurrent = 5
page_limit = 50
default_query_id = ""
use_custom_distribution_algorithm = false

[api.default_options]
distrib = "true"
latest = "true"
replica = "none"
retracted = "false"

[plugins]
enabled = false
```

I changed the index node:
```console
Grey@Audron:seaicecp$ esgpull config api.index_node esgf-node.ornl.gov/esgf-1-5-bridge
[api]
index_node = "esgf-node.ornl.gov/esgf-1-5-bridge"

👍 New config file created at /Volumes/BERGY_BITS/seaicecp_data/.esgpull/config.toml.
```

I confirmed the config changed.
```console
Grey@Audron:seaicecp$ esgpull config
─────────────────────────── /Volumes/BERGY_BITS/seaicecp_data/.esgpull/config.toml ───────────────────────────
[paths]
data = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/data"
db = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/db"
log = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/log"
tmp = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/tmp"
plugins = "/Volumes/BERGY_BITS/seaicecp_data/.esgpull/plugins"

[credentials]
filename = "credentials.toml"

[cli]
page_size = 20

[db]
filename = "esgpull.db"

[download]
chunk_size = 67108864
http_timeout = 20
max_concurrent = 5
disable_ssl = false
disable_checksum = false
show_filename = false

[api]
index_node = "esgf-node.ornl.gov/esgf-1-5-bridge"
http_timeout = 20
max_concurrent = 5
page_limit = 50
default_query_id = ""
use_custom_distribution_algorithm = false

[api.default_options]
distrib = "true"
latest = "true"
replica = "none"
retracted = "false"

[plugins]
enabled = false
```

Great, it changed. 
Then I tried a search again.
```console
Grey@Audron:seaicecp$ bash esgpull_searches/HRMIP_hist_areacello.sh 
Found 16 datasets.
 id │                              dataset                               │ # │   size    │     data_node      
════╪════════════════════════════════════════════════════════════════════╪═══╪═══════════╪════════════════════
  0 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-LR.hist-1950.r1i1p1f2.Ofx.areacel… │ 1 │  23.4 MiB │ eagle.alcf.anl.gov 
  1 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.hist-1950.r1i1p1f1.Ofx.area… │ 1 │  31.6 MiB │ eagle.alcf.anl.gov 
  2 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.hist-1950.r1i1p1f1.Ofx.area… │ 1 │  31.6 MiB │ esgf-node.ornl.gov 
  3 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.hist-1950.r1i1p1f1.Ofx.are… │ 1 │  63.1 MiB │ eagle.alcf.anl.gov 
  4 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-HR.hist-1950.r1i1p1f2.Ofx.areacel… │ 1 │ 256.9 MiB │ eagle.alcf.anl.gov 
  5 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-LR.hist-1950.r1i1p1f2.Ofx.areacel… │ 1 │  23.4 MiB │ esgf-node.ornl.gov 
  6 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.hist-1950.r1i1p1f1.Ofx.area… │ 1 │  31.6 MiB │ esgf-node.ornl.gov 
  7 │ CMIP6.HighResMIP.BCC.BCC-CSM2-HR.hist-1950.r1i1p1f1.Ofx.areacello… │ 1 │  11.4 MiB │    cmip.bcc.cma.cn 
  8 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.hist-1950.r1i1p1f1.Ofx.are… │ 1 │  63.1 MiB │ esgf-node.ornl.gov 
  9 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-HR.hist-1950.r1i1p1f2.Ofx.areacel… │ 1 │ 256.9 MiB │ esgf-node.ornl.gov 
 10 │ CMIP6.HighResMIP.BCC.BCC-CSM2-HR.hist-1950.r1i1p1f1.Ofx.areacello… │ 1 │  11.4 MiB │ esgf-node.ornl.gov 
 11 │ CMIP6.HighResMIP.BCC.BCC-CSM2-HR.hist-1950.r1i1p1f1.Ofx.areacello… │ 1 │  11.4 MiB │ eagle.alcf.anl.gov 
 12 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL.hist-1950.r1i1p1f1.Ofx.area… │ 1 │   1.4 MiB │ esgf-node.ornl.gov 
 13 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL.hist-1950.r1i1p1f1.Ofx.area… │ 1 │   1.4 MiB │ eagle.alcf.anl.gov 
 14 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.hist-1950.r1i1p1f1.Ofx.area… │ 1 │  31.6 MiB │ eagle.alcf.anl.gov 
 15 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.hist-1950.r1i1p1f1.Ofx.are… │ 1 │  63.1 MiB │ esgf-data.ucar.edu
```

#### Adding `esgpull` to the package

After doing the above, I noticed that `esgpull` had not been added to the `.toml` file.
I added it with the `uv add esgpull` command as shown below.
I'm not sure whether it would be possible to just do this instead of the `uv tool install` command I did above.

```console
(seaicecp) Grey@Audron:seaicecp$ uv add esgpull
Resolved 137 packages in 1.73s
      Built seaicecp @ file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp
Prepared 4 packages in 669ms
Uninstalled 1 package in 7ms
Installed 28 packages in 162ms
 + aiofiles==25.1.0
 + aiostream==0.7.1
 + alembic==1.18.4
 + annotated-types==0.7.0
 + anyio==4.13.0
 + cattrs==26.1.0
 + cffi==2.0.0
 + click-params==0.5.0
 + cryptography==46.0.7
 + deprecated==1.3.1
 + esgpull==0.9.6
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + mako==1.3.11
 + pycparser==3.0
 + pydantic==2.13.3
 + pydantic-core==2.46.3
 + pydantic-settings==2.14.0
 + pyopenssl==26.0.0
 + python-dotenv==1.2.2
 + rich==15.0.0
 ~ seaicecp==0.1.0 (from file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp)
 + setuptools==82.0.1
 + tomlkit==0.14.0
 + typing-inspection==0.4.2
 + validators==0.22.0
 + wrapt==2.1.2
(seaicecp) Grey@Audron:seaicecp$ esgpull --version
esgpull, version 0.9.6
```

<a id='jupyter_notebook'></a>
[back to top](#top)

### Using a Jupyter notebook

I'm now following the `uv` guide on [Using `uv` with Jupyter](https://docs.astral.sh/uv/guides/integration/jupyter/). I'm actually also following the Medium blog post [Create virtual environments with UV to use Jupyter Notebooks inside VS Code](https://medium.com/@luismarcelobp/create-virtual-environments-with-uv-to-use-jupyter-notebooks-inside-vs-code-48f336023e7f).

```console
Grey@Audron:seaicecp$ source .venv/bin/activate
(seaicecp) Grey@Audron:seaicecp$ uv add --dev ipykernel
Resolved 76 packages in 1.08s
Prepared 26 packages in 1.47s
Installed 26 packages in 178ms
 + appnope==0.1.4
 + asttokens==3.0.1
 + comm==0.2.3
 + debugpy==1.8.20
 + decorator==5.2.1
 + executing==2.2.1
 + ipykernel==7.2.0
 + ipython==9.12.0
 + ipython-pygments-lexers==1.1.1
 + jedi==0.19.2
 + jupyter-client==8.8.0
 + jupyter-core==5.9.1
 + matplotlib-inline==0.2.1
 + nest-asyncio==1.6.0
 + parso==0.8.6
 + pexpect==4.9.0
 + platformdirs==4.9.6
 + prompt-toolkit==3.0.52
 + psutil==7.2.2
 + ptyprocess==0.7.0
 + pure-eval==0.2.3
 + pygments==2.20.0
 + pyzmq==27.1.0
 + stack-data==0.6.3
 + traitlets==5.14.3
 + wcwidth==0.6.0
(seaicecp) Grey@Audron:seaicecp$ uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=seaicecp_kernel
Installed kernelspec seaicecp_kernel in /Users/Grey/Library/Jupyter/kernels/seaicecp_kernel
```

At this point, I restarted VSCodium. Then, I made a notebook called `testing.ipynb`, then tried to import `xarray`. This brought up a dialogue where I didn't see `seaicecp_kernel`, but I selected ".venv (Python 3.14.1) .venv/bin/python". I then successfully imported `xarray` and `geoviews`. However, I encoutered the following error when I tried to open the dataset:

<a id='cdo_install'></a>
[back to top](#top)

### Adding `cdo`

I also added `cdo` (Climate Data Operators) to be able to interpolate the irregular grid of the model data onto a regular grid for plotting.

```console
(seaicecp) Grey@Audron:seaicecp$ uv add cdo
Resolved 138 packages in 469ms
      Built seaicecp @ file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp
Prepared 2 packages in 113ms
Uninstalled 1 package in 1ms
Installed 2 packages in 7ms
 + cdo==1.6.1
 ~ seaicecp==0.1.0 (from file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp)
(seaicecp) Grey@Audron:seaicecp$ cdo --version
bash: cdo: command not found
```

As it turns out, the command I used above only installed the Python package `cdo`, but not the actual `cdo` command line tool which is required for the Python package to work.
On the [`cdo` installation page for MacOS](https://code.mpimet.mpg.de/projects/cdo/wiki/MacOS_Platform), they show using Homebrew to install `cdo`.
```console
(seaicecp) Grey@Audron:seaicecp$ brew install cdo
```

<details>

<summary>Output from the above command</summary>

```console
==> Auto-updating Homebrew...
Adjust how often this is run with `$HOMEBREW_AUTO_UPDATE_SECS` or disable with
`$HOMEBREW_NO_AUTO_UPDATE=1`. Hide these hints with `$HOMEBREW_NO_ENV_HINTS=1` (see `man brew`).
==> Auto-updated Homebrew!
Updated 2 taps (homebrew/core and homebrew/cask).
==> New Formulae
cc-connect: Bridges local AI coding agents to messaging platforms
openssl@4: Cryptography and SSL/TLS Toolkit
==> New Casks
cavalry: Procedural motion design and animation software
font-bjcree
font-estedad
mujoco: General purpose physics engine
openin: Route links, emails, and files to your preferred apps
t3-code@nightly: Minimal GUI for AI code agents

You have 112 outdated formulae installed.

==> Fetching downloads for: cdo
✔︎ Bottle Manifest cdo (2.6.0)                                                           Downloaded   30.2KB/ 30.2KB
✔︎ Bottle Manifest isl (0.27)                                                            Downloaded   14.5KB/ 14.5KB
✔︎ Bottle isl (0.27)                                                                     Downloaded    1.8MB/  1.8MB
✔︎ Bottle Manifest mpfr (4.2.2)                                                          Downloaded   12.7KB/ 12.7KB
✔︎ Bottle mpfr (4.2.2)                                                                   Downloaded    1.1MB/  1.1MB
✔︎ Bottle Manifest libmpc (1.4.1)                                                        Downloaded   12.0KB/ 12.0KB
✔︎ Bottle libmpc (1.4.1)                                                                 Downloaded  164.3KB/164.3KB
✔︎ Bottle Manifest xz (5.8.3)                                                            Downloaded   11.8KB/ 11.8KB
✔︎ Bottle xz (5.8.3)                                                                     Downloaded  752.9KB/752.9KB
✔︎ Bottle Manifest zstd (1.5.7_1)                                                        Downloaded   13.2KB/ 13.2KB
✔︎ Bottle zstd (1.5.7_1)                                                                 Downloaded  929.3KB/929.3KB
✔︎ Bottle Manifest gcc (15.2.0_1)                                                        Downloaded   23.5KB/ 23.5KB
✔︎ Bottle Manifest libaec (1.1.6)                                                        Downloaded    7.2KB/  7.2KB
✔︎ Bottle libaec (1.1.6)                                                                 Downloaded   49.9KB/ 49.9KB
✔︎ Bottle Manifest libpng (1.6.58)                                                       Downloaded    8.6KB/  8.6KB
✔︎ Bottle libpng (1.6.58)                                                                Downloaded  455.9KB/455.9KB
✔︎ Bottle Manifest hdf5 (2.1.1)                                                          Downloaded   20.7KB/ 20.7KB
✔︎ Bottle Manifest netcdf (4.10.0)                                                       Downloaded   24.4KB/ 24.4KB
✔︎ Bottle netcdf (4.10.0)                                                                Downloaded    1.3MB/  1.3MB
✔︎ Bottle Manifest jpeg-turbo (3.1.4.1)                                                  Downloaded    8.4KB/  8.4KB
✔︎ Bottle jpeg-turbo (3.1.4.1)                                                           Downloaded    1.2MB/  1.2MB
✔︎ Bottle Manifest libtiff (4.7.1_1)                                                     Downloaded   12.6KB/ 12.6KB
✔︎ Bottle Manifest little-cms2 (2.18)                                                    Downloaded   12.2KB/ 12.2KB
✔︎ Bottle little-cms2 (2.18)                                                             Downloaded  426.1KB/426.1KB
✔︎ Bottle Manifest openjpeg (2.5.4)                                                      Downloaded   14.0KB/ 14.0KB
✔︎ Bottle Manifest eccodes (2.46.0)                                                      Downloaded   32.8KB/ 32.8KB
✔︎ Bottle libtiff (4.7.1_1)                                                              Downloaded    1.9MB/  1.9MB
✔︎ Bottle Manifest proj (9.8.1)                                                          Downloaded   20.1KB/ 20.1KB
✔︎ Bottle openjpeg (2.5.4)                                                               Downloaded    2.3MB/  2.3MB
✔︎ Bottle cdo (2.6.0)                                                                    Downloaded    3.7MB/  3.7MB
✔︎ Bottle hdf5 (2.1.1)                                                                   Downloaded    9.0MB/  9.0MB
✔︎ Bottle eccodes (2.46.0)                                                               Downloaded   11.1MB/ 11.1MB
✔︎ Bottle gcc (15.2.0_1)                                                                 Downloaded  161.9MB/161.9MB
✔︎ Bottle proj (9.8.1)                                                                   Downloaded  800.1MB/800.1MB
==> Installing dependencies for cdo: isl, mpfr, libmpc, xz, zstd, gcc, libaec, libpng, hdf5, netcdf, jpeg-turbo, libtiff, little-cms2, openjpeg, eccodes and proj
==> Installing cdo dependency: isl
==> Pouring isl--0.27.sequoia.bottle.tar.gz
🍺  /usr/local/Cellar/isl/0.27: 74 files, 8MB
==> Installing cdo dependency: mpfr
==> Pouring mpfr--4.2.2.sequoia.bottle.tar.gz
🍺  /usr/local/Cellar/mpfr/4.2.2: 31 files, 3.3MB
==> Installing cdo dependency: libmpc
==> Pouring libmpc--1.4.1.sequoia.bottle.tar.gz
🍺  /usr/local/Cellar/libmpc/1.4.1: 14 files, 512.1KB
==> Installing cdo dependency: xz
==> Pouring xz--5.8.3.sequoia.bottle.tar.gz
🍺  /usr/local/Cellar/xz/5.8.3: 96 files, 2.5MB
==> Installing cdo dependency: zstd
==> Pouring zstd--1.5.7_1.sequoia.bottle.tar.gz
🍺  /usr/local/Cellar/zstd/1.5.7_1: 32 files, 2.5MB
==> Installing cdo dependency: gcc
==> Pouring gcc--15.2.0_1.sequoia.bottle.tar.gz
🍺  /usr/local/Cellar/gcc/15.2.0_1: 1,715 files, 499.7MB
==> Installing cdo dependency: libaec
==> Pouring libaec--1.1.6.sonoma.bottle.tar.gz
Warning: These files were overwritten during the `brew link` step:
/usr/local/include/szlib.h
/usr/local/lib/libsz.2.dylib
/usr/local/lib/libsz.a
/usr/local/lib/libsz.dylib

They have been backed up to: /Users/Grey/Library/Caches/Homebrew/Backup
==> Summary
🍺  /usr/local/Cellar/libaec/1.1.6: 23 files, 176.1KB
==> Installing cdo dependency: libpng
==> Pouring libpng--1.6.58.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/libpng/1.6.58: 28 files, 1.3MB
==> Installing cdo dependency: hdf5
==> Pouring hdf5--2.1.1.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/hdf5/2.1.1: 271 files, 20.7MB
==> Installing cdo dependency: netcdf
==> Pouring netcdf--4.10.0.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/netcdf/4.10.0: 34 files, 4.0MB
==> Installing cdo dependency: jpeg-turbo
==> Pouring jpeg-turbo--3.1.4.1.sonoma.bottle.tar.gz
Warning: These files were overwritten during the `brew link` step:
/usr/local/bin/cjpeg
/usr/local/bin/djpeg
/usr/local/bin/jpegtran
/usr/local/bin/rdjpgcom
/usr/local/bin/wrjpgcom
/usr/local/include/jconfig.h
/usr/local/include/jerror.h
/usr/local/include/jmorecfg.h
/usr/local/include/jpeglib.h
/usr/local/share/man/man1/cjpeg.1
/usr/local/share/man/man1/djpeg.1
/usr/local/share/man/man1/jpegtran.1
/usr/local/share/man/man1/rdjpgcom.1
/usr/local/share/man/man1/wrjpgcom.1
/usr/local/lib/libjpeg.a
/usr/local/lib/libjpeg.dylib
/usr/local/lib/pkgconfig/libjpeg.pc

They have been backed up to: /Users/Grey/Library/Caches/Homebrew/Backup
==> Summary
🍺  /usr/local/Cellar/jpeg-turbo/3.1.4.1: 47 files, 4.4MB
==> Installing cdo dependency: libtiff
==> Pouring libtiff--4.7.1_1.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/libtiff/4.7.1_1: 488 files, 8.2MB
==> Installing cdo dependency: little-cms2
==> Pouring little-cms2--2.18.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/little-cms2/2.18: 23 files, 1.2MB
==> Installing cdo dependency: openjpeg
==> Pouring openjpeg--2.5.4.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/openjpeg/2.5.4: 512 files, 14.6MB
==> Installing cdo dependency: eccodes
==> Pouring eccodes--2.46.0.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/eccodes/2.46.0: 23,096 files, 56.7MB
==> Installing cdo dependency: proj
==> Pouring proj--9.8.1.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/proj/9.8.1: 530 files, 834.3MB
==> Installing cdo
==> Pouring cdo--2.6.0.sonoma.bottle.tar.gz
🍺  /usr/local/Cellar/cdo/2.6.0: 9 files, 11.2MB
==> Running `brew cleanup cdo`...
Disable this behaviour by setting `HOMEBREW_NO_INSTALL_CLEANUP=1`.
Hide these hints with `HOMEBREW_NO_ENV_HINTS=1` (see `man brew`).
```

</details>

Then, I can check to make sure `cdo` is installed by checking the version.
```console
(seaicecp) Grey@Audron:seaicecp$ cdo --version
Climate Data Operators version 2.6.0 (https://mpimet.mpg.de/cdo)
System: x86_64-apple-darwin23.6.0
CXX Compiler: clang++ -std=gnu++11 -std=gnu++20 -g -O2  -pthread
CXX version : Apple clang version 16.0.0 (clang-1600.0.26.6)
CXX library :
C Compiler: clang -g -O2  -pthread -pthread
C version : Apple clang version 16.0.0 (clang-1600.0.26.6)
F77 Compiler: gfortran -g -O2
F77 version : GNU Fortran (Homebrew GCC 15.2.0_1) 15.2.0
Features: 32GB 8threads c++20 Fortran pthreads HDF5 NC4/HDF5 dap sz proj sse4_2
Libraries: yac/3.13.1 NetCDF/4.10.0 HDF5/2.1.1(h2.0.0) proj/9.7.1
CDI data types: SizeType=size_t
CDI file types: srv ext ieg grb1 grb2 nc1 nc2 nc4 nc4c nc5 nczarr 
     CDI library version : 2.6.0
 cgribex library version : 2.3.1
 ecCodes library version : 2.46.0
  NetCDF library version : 4.10.0 of Feb 25 2026 17:25:46 $
    exse library version : 2.0.0
    FILE library version : 1.9.1
```


<a id='build_pkg'></a>
[back to top](#top)

## Building the package

As shown in the [Build systems](https://docs.astral.sh/uv/concepts/projects/config/#build-systems) documentation for `uv`, I used the `--package` flag when initializing the repository. 
In the [Building your package](https://docs.astral.sh/uv/guides/package/#building-your-package) section, I used the 

```console
$ uv sync
Resolved 78 packages in 550ms
      Built seaicecp @ file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp
Prepared 1 package in 53ms
Installed 1 package in 12ms
 + seaicecp==0.1.0 (from file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp)
(seaicecp) Grey@Audron:seaicecp$ uv lock
Resolved 78 packages in 21ms
```

```console
(seaicecp) Grey@Audron:seaicecp$ uv build
Building source distribution (uv build backend)...
Building wheel from source distribution (uv build backend)...
Successfully built dist/seaicecp-0.1.0.tar.gz
Successfully built dist/seaicecp-0.1.0-py3-none-any.whl
```



```console
(seaicecp) Grey@Audron:seaicecp$ uv version
seaicecp 0.1.0
```

I can now import the package in a Jupyter notebook.
```python
import seaicecp 
print(seaicecp.__version__)
```
```console
0.1.0
```

<a id='docs'></a>
[back to top](#top)

## Documentation

<a id='build_docs'></a>
[back to top](#top)

### Building documentation

Adding necessary packages as shown in [3.8.4. Building documentation](https://py-pkgs.org/03-how-to-package-a-python#building-documentation).
```console
Grey@Audron:seaicecp$ source .venv/bin/activate
(seaicecp) Grey@Audron:seaicecp$ uv add --dev myst-nb sphinx-autoapi sphinx-rtd-theme
Resolved 112 packages in 1.08s
      Built seaicecp @ file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp
Prepared 31 packages in 3.20s
Uninstalled 1 package in 8ms
Installed 35 packages in 317ms
 + alabaster==1.0.0
 + astroid==4.1.2
 + attrs==26.1.0
 + babel==2.18.0
 + click==8.3.2
 + docutils==0.22.4
 + fastjsonschema==2.21.2
 + greenlet==3.4.0
 + imagesize==2.0.0
 + importlib-metadata==9.0.0
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 + jupyter-cache==1.0.1
 + myst-nb==1.4.0
 + myst-parser==5.0.0
 + nbclient==0.10.4
 + nbformat==5.10.4
 + referencing==0.37.0
 + roman-numerals==4.1.0
 + rpds-py==0.30.0
 ~ seaicecp==0.1.0 (from file:///Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp)
 + snowballstemmer==3.0.1
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
 + tabulate==0.10.0
 + zipp==3.23.1
```

Then, building the docs. It is necessary to have the environment activated for this step. 
```console
(seaicecp) Grey@Audron:seaicecp$ cd docs
(seaicecp) Grey@Audron:docs$ make html
Running Sphinx v9.1.0
loading translations [en]... done
making output directory... done
myst v5.0.0: MdParserConfig(commonmark_only=False, gfm_only=False, enable_extensions=set(), disable_syntax=[], all_links_external=False, links_external_new_tab=False, url_schemes=('http', 'https', 'mailto', 'ftp'), ref_domains=None, fence_as_directive=set(), number_code_blocks=[], title_to_header=False, heading_anchors=0, heading_slug_func=None, html_meta={}, footnote_sort=True, footnote_transition=True, words_per_minute=200, substitutions={}, linkify_fuzzy_links=True, dmath_allow_labels=True, dmath_allow_space=True, dmath_allow_digits=True, dmath_double_inline=False, update_mathjax=True, mathjax_classes='tex2jax_process|mathjax_process|math|output_area', enable_checkboxes=False, suppress_warnings=[], highlight_code_blocks=True)
myst-nb v1.4.0: NbParserConfig(custom_formats={}, metadata_key='mystnb', cell_metadata_key='mystnb', kernel_rgx_aliases={}, eval_name_regex='^[a-zA-Z_][a-zA-Z0-9_]*$', execution_mode='auto', execution_cache_path='', execution_excludepatterns=(), execution_timeout=30, execution_in_temp=False, execution_allow_errors=False, execution_raise_on_error=False, execution_show_tb=False, merge_streams=False, render_plugin='default', remove_code_source=False, remove_code_outputs=False, scroll_outputs=False, code_prompt_show='Show code cell {type}', code_prompt_hide='Hide code cell {type}', number_source_lines=False, output_stderr='show', render_text_lexer='myst-ansi', render_error_lexer='ipythontb', render_image_options={}, render_figure_options={}, render_markdown_format='commonmark', output_folder='build', append_css=True, metadata_to_fm=False)
Using jupyter-cache at: /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/_build/.jupyter_cache
[AutoAPI] Reading files... [ 50%] /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/src/
[AutoAPI] Reading files... [100%] /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/src/seaicecp/__init__.py
[AutoAPI] Mapping Data... [ 50%] /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/src/s
[AutoAPI] Mapping Data... [100%] /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/src/seaicecp/__init__.py
[AutoAPI] Rendering Data... [ 50%] seaicecp
[AutoAPI] Rendering Data... [100%] seaicecp.seaicecp

[autosummary] generating autosummary for: changelog.md, conduct.md, contributing.md, example.ipynb, index.md
building [mo]: targets for 0 po files that are out of date
writing output... 
building [html]: targets for 5 source files that are out of date
updating environment: [new config] 8 added, 0 changed, 0 removed
/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/example.ipynb: Executing notebook using local CWD [mystnb]
/Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/example.ipynb: Executed notebook in 1.85 seconds [mystnb]
reading sources... [100%] index
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
copying assets... 
copying static files... 
Writing evaluated template result to /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/_build/html/_static/basic.css
Writing evaluated template result to /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/_build/html/_static/language_data.js
Writing evaluated template result to /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/_build/html/_static/documentation_options.js
Writing evaluated template result to /Users/Grey/Documents/Research/Postdoc_Projects/York_U_sea_ice/seaicecp/docs/_build/html/_static/js/versions.js
copying static files: done
copying extra files... 
copying extra files: done
copying assets: done
writing output... [100%] index
generating indices... genindex py-modindex done
highlighting module code... [100%] seaicecp.seaicecp
writing additional pages... search done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.

The HTML pages are in _build/html.
```

Then, I went into the `docs/html/index.html` in VSCodium, hit the preview button, then the top right menu to open the page in a browser.
The test webpage seems like it rendered properly. 

<a id='host_docs'></a>
[back to top](#top)

### Hosting documentation

Following [3.8.5. Hosting documentation online](https://py-pkgs.org/03-how-to-package-a-python#hosting-documentation-online).

First, a few changes need to be made to the `.yaml` file to ensure the documentation can successfully be hosted. 
Upon generating the `cookiecutter` files, the configuration for Read the Docs looked like this:
```yaml
# .readthedocs.yaml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Set the OS, Python version and other tools you might need
build:
  os: ubuntu-22.04
  tools:
    python: "3.14.1"
  jobs:
    post_create_environment:
      # Install poetry
      # https://python-poetry.org/docs/#installing-manually
      - pip install poetry
    post_install:
      - VIRTUAL_ENV=$READTHEDOCS_VIRTUALENV_PATH poetry install --all-groups

# Build documentation in the "docs/" directory with Sphinx
sphinx:
  configuration: docs/conf.py
```

Two changes need to be made here. 
The first is to specify the version of Python as `3.14` instead of `3.14.1` as Read the Docs only recognizes up to the minor version number, not the patch number.
Second, the `jobs` section needs to be changed to use `uv` instead of `poetry`.
I followed an example shown in [Issue #11289, Support uv](https://github.com/readthedocs/readthedocs.org/issues/11289) posted on the Read the Docs GitHub page. 
```yaml
# .readthedocs.yaml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Set the OS, Python version and other tools you might need
build:
  os: ubuntu-22.04
  tools:
    python: "3.14.1"
  jobs:
    pre_create_environment:
      - asdf plugin add uv
      - asdf install uv latest
      - asdf global uv latest
    create_environment:
      - uv venv $READTHEDOCS_VIRTUALENV_PATH
    install:
      # Use a cache dir in the same mount to halve the install time
      - VIRTUAL_ENV=$READTHEDOCS_VIRTUALENV_PATH uv pip install --cache-dir $READTHEDOCS_VIRTUALENV_PATH/../../uv_cache -r docs/requirements.txt

# Build documentation in the "docs/" directory with Sphinx
sphinx:
  configuration: docs/conf.py

```

Next, I went to [Read the Docs](https://readthedocs.org/) and logged in. 
On the "Projects" dashboard, I clicked "Add project."
On the next page, I selected "Configure manually" then filled in this information:
- Name
    - `seaicecp`
- Repository URL
    - `https://github.com/scheemik/seaicecp`
- Default branch
    - `main`
- Language
    - English

Then, I clicked "Next" and confirmed that the file `.readthedocs.yaml` exists (from using the `cookiecutter` when initializing the repository) and clicked "This file exists."
Upon building, I was greeted with confirmation that the build succeeded. 
```
Version latest / Builds / #32314755 
	git clone --depth 1 https://github.com/scheemik/seaicecp .
	git fetch origin --force --prune --prune-tags --depth 50 refs/heads/main:refs/remotes/origin/main
	git checkout --force origin/main
	cat .readthedocs.yml
	asdf global python 3.14.0
	asdf plugin add uv
	asdf install uv latest
	asdf global uv latest
	uv venv $READTHEDOCS_VIRTUALENV_PATH
	VIRTUAL_ENV=$READTHEDOCS_VIRTUALENV_PATH uv pip install --cache-dir $READTHEDOCS_VIRTUALENV_PATH/../../uv_cache -r docs/requirements.txt
	python -m sphinx -T -j auto -b html -d _build/doctrees -D language=en . $READTHEDOCS_OUTPUT/html
```

Now, the documentation for this project is live and available to view at https://seaicecp.readthedocs.io/en/latest/.
I put that URL in the "About" section of the GitHub repository under "Website."

<a id='latex_syntax'></a>
[back to top](#top)

### Enabling $\LaTeX$ math syntax

In order to be able to use dollar signs to quickly indicate a mathematical symbol from $\LaTeX$, I added the `dollarmath` and `amsmath` extensions to the `docs/conf.py` file's `myst_enable_extensions` list.
```python
myst_enable_extensions = [
    "dollarmath", 
    "amsmath"
]
```

See the MyST-Parser documentation page on [Syntax Extensions](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html)

<a id='doi_links'></a>
[back to top](#top)

### Enabling easy DOI links

Added to `docs/conf.py`:
```python
myst_url_schemes = {
    "http": None,
    "https": None,
    "wiki": "https://en.wikipedia.org/wiki/{{path}}#{{fragment}}",
    "doi": "https://doi.org/{{path}}",
    "gh-issue": {
        "url": "https://github.com/executablebooks/MyST-Parser/issue/{{path}}#{{fragment}}",
        "title": "Issue #{{path}}",
        "classes": ["github"],
    },
}
```

See the MyST-Parser documentation page on [Customizing external URL resolution](https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html#customising-external-url-resolution)