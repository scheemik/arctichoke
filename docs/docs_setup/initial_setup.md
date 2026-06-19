# Initial Setup

This guide details how the architecture of this project was developed.
For streamlined instructions on how to install and start using this project, see the {doc}`Installation <installation>` page.

The structure of this project is based on the incredibly helpful guide, [Py-Pkgs](https://py-pkgs.org/welcome).
Several of the sections below are summarizations of parts of that guide, with details of the changes I made for this specific setup. 

## Contents

- [The order of operations](#the-order-of-operations)
- [The `uv` package manager](#the-uv-package-manager)
- [Creating a package structure](#creating-a-package-structure)
    - [Using `uv init`](#using-uv-init)
    - [Using a `cookiecutter` template](#using-a-cookiecutter-template)
    - [Combining `uv` and `cookiecutter` structures](#combining-uv-and-cookiecutter-structures)
- [Version control and GitHub](#version-control-and-github)
    - [Setting the default branch](#setting-the-default-branch)
- [Podman](#podman)
    - [Installing Podman](#installing-podman)
    - [Testing Podman](#testing-podman)
    - [Pod Manager extension for VSCodium](#pod-manager-extension-for-vscodium)
    - [Building a simple container](#building-a-simple-container)
    - [The `Containerfile`](#the-containerfile)
        - [Pinning the versions of `uv` and `trixie-slim`](#pinning-the-versions-of-uv-and-trixie-slim)
        - [Defining environment variables](#defining-environment-variables)
        - [Installing system and scientific dependencies](#installing-system-and-scientific-dependencies)
        - [Preparing Python, `uv`, and the working directory](#preparing-python-uv-and-the-working-directory)
        - [`uv` dependencies and Jupyter kernel](#uv-dependencies-and-jupyter-kernel)
        - [Downloading commonly used Natural Earth shapefiles](#downloading-commonly-used-natural-earth)
        - [Setting up `esgpull` install](#setting-up-esgpull-install)
        - [Setting up the Jupyter server](#setting-up-the-jupyter-server)
    - [The `start_container` script](#the-start_container-script)
        - [Set the script to fail on common errors](#set-the-script-to-fail-on-common-errors)
        - [Ensure the virtual machine is running](#ensure-the-virtual-machine-is-running)
        - [Set the parameters](#set-the-parameters)
        - [Check existing containers and images](#check-existing-containers-and-images)
        - [Set up access to external volumes](#set-up-access-to-external-volumes)
        - [Create the list of volumes](#create-the-list-of-volumes)
        - [Run the container](#run-the-container)
    - [Testing the container](#testing-the-container)
    - [Cleaning up old images](#cleaning-up-old-images)
- [Virtual environment and packages](#virtual-environment-and-packages)
    - [Activating the virtual environment](#activating-the-virtual-environment)
    - [Adding package dependencies](#adding-package-dependencies)
        - [Packages for datasets](#packages-for-datasets)
        - [Packages for making plots](#packages-for-making-plots)
        - [Packages for saving plots](#packages-for-saving-plots)
        - [Packages for Jupyter notebooks](#packages-for-jupyter-notebooks)
        - [Packages for external tools](#packages-for-external-tools)
        - [Packages for testing](#packages-for-testing)
        - [Packages for documentation](#packages-for-documentation)
    - [The `.pyproject.toml` file](#the-pyprojecttoml-file)
    - [Building the package](#building-the-package)
    - [Using a Jupyter notebook in the container](#using-a-jupyter-notebook-in-the-container)
    - [Initializing `esgpull`](#initializing-esgpull)
        - [Creating an `esgpull` install](#creating-an-esgpull-install)
        - [Configuring the `esgpull` install](#configuring-the-esgpull-install)
- [Documentation](#documentation)
    - [Building documentation](#building-documentation)
    - [Hosting documentation](#hosting-documentation)
    - [Enabling $\LaTeX$ math syntax](#enabling--math-syntax)
    - [Enabling easy DOI links](#enabling-easy-doi-links)

---

## The order of operations
[back to top](#initial-setup)

When initially setting up this project, I installed the [`uv` package manager](#the-uv-package-manager), [created the package structure](#creating-a-package-structure) of the project, and [added Python package dependencies](#adding-package-dependencies) all before writing the [Podman](#podman) container.
It is likely that one could avoid installing `uv` on their host system by first setting up the container and, once inside the container, create the package structure.
However, I present those steps first as I have not tested that possibility and thus present them in the manner I followed, outside the container.
I do, however, place the section on the [virtual environment and installing package dependencies](#virtual-environment-and-packages) after creating the container in this document because I have confirmed that adding packages with `uv` inside the container works.

---

## The `uv` package manager
[back to top](#initial-setup)

In [Py-Pkgs Chapter 2](https://py-pkgs.org/02-setup), they suggest to use Miniconda to create an environment and use [`poetry`](https://python-poetry.org/) to manage dependencies. 
For this project, I decided to use [`uv`](https://docs.astral.sh/uv/) instead. 
From the instructions for [Installing `uv`](https://docs.astral.sh/uv/getting-started/installation/), I used Homebrew.
I've truncated the output below for brevity. 
```console
user@local:~$ brew install uv
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
user@local:~$ brew upgrade uv
Warning: uv 0.11.6 already installed
```


---

## Creating a package structure
[back to top](#initial-setup)


### Using `uv init`
[back to top](#initial-setup)

To start a project, I simply need to use `uv` to initiate one, following the [Working on projects](https://docs.astral.sh/uv/guides/projects/) guide.
I chose the name `seaicecp` to stand for "Sea Ice Choke Points," trying to balance brevity and descriptiveness.
First, I navigated to the directory in which I want my project to be, `<absolute/path/to/project>`, then used the `uv init` command with the name for the project and the `--package` flag.
```console
user@local:~$ cd /<absolute/path/to/project>
user@local:/<absolute/path/to/project>$ uv init seaicecp --package
Initialized project `seaicecp` at `/<absolute/path/to/project>/seaicecp`
```

This creates a very simple directory structure for the project.
```console
user@local:/<absolute/path/to/project>$ tree seaicecp
├── .gitignore
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```


### Using a `cookiecutter` template
[back to top](#initial-setup)

In [Py-Pkgs Section 2.2.2](https://py-pkgs.org/02-setup#install-packaging-software), they suggest installing `cookiecutter` to create a package from a pre-made template. 
This package is then actually used in [Section 3.2.2](https://py-pkgs.org/03-how-to-package-a-python#creating-a-package-structure). 
I do like the package structure they provide with their `cookiecutter` template, but I will need to integrate it with the directory structure generated above with `uv init` as their template assumes using `poetry` as a dependency manager.

`uv` comes the ability to [invoke a tool without installing it by using `uvx`](https://docs.astral.sh/uv/guides/tools/#running-tools). 
This is helpful when trying something out, or when using a tool that is just for an initial set up, like [`cookiecutter`](https://github.com/cookiecutter/cookiecutter), which can be used to create a package structure.
By using `uvx`, you don't need to commit to actually installing `cookiecutter` on your system.

First, I created and went into a temporary directory, `tmp_dir`, then generated the package structure.
This is to ensure I didn't accidentally overwrite the structure I made with `uv init` earlier.
```console
user@local:seaicecp$ mkdir tmp_dir
user@local:seaicecp$ cd tmp_dir
user@local:tmp_dir$ git branch -m master main
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
user@local:tmp_dir$ tree seaicecp/
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


### Combining `uv` and `cookiecutter` structures
[back to top](#initial-setup)

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
user@local:tmp_dir$ cd ..
user@local:seaicecp$ rm -rf tmp_dir/
```


## Version control and GitHub
[back to top](#initial-setup)

Following [Py-Pkgs Section 3.3. Put your package under version control](https://py-pkgs.org/03-how-to-package-a-python#put-your-package-under-version-control), I initiated `git` for my new repository.
```console
user@local:seaicecp$ git init
Initialized empty Git repository in /<absolute/path/to/project>/seaicecp/.git/
```

I then added and committed the initial structure and pushed to a new [GitHub repository for the project](https://github.com/scheemik/seaicecp).
I am working in VSCodium, which I'd already set up to [connect to my GitHub account](https://github.com/VSCodium/vscodium/blob/master/docs/usage.md#signin-github), so the process was as simple as pressing the "push" button in the GUI.


### Setting the default branch
[back to top](#initial-setup)

For the version of `git` I have, it still sets the default branch as `master` instead of `main`. 
I'm following the guide from Geeks for Geeks on [How to Change Git Default Branch From Master?](https://www.geeksforgeeks.org/git/how-to-change-git-default-branch-from-master/)

First, I renamed the local branch.
```console
user@local:/<absolute/path/to/project>$ cd seaicecp
user@local:seaicecp$ git branch -m master main
user@local:seaicecp$ git push -u origin main
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
user@local:seaicecp$ git push origin --delete master
To https://github.com/scheemik/seaicecp.git
 - [deleted]         master
```

Since the repository had not been cloned anywhere else at this point, that was all I needed to do.

---

## Podman
[back to top](#initial-setup)

[Podman](https://podman.io/) is an open-source tool by [Red Hat](https://www.redhat.com/en0) for creating and managing containers, similar to [Docker](https://www.docker.com/).
[Containerization](https://en.wikipedia.org/wiki/Containerization_(computing)) allows the creation of isolated, reproducible computing environments, making it easier to ensure code will run the same way across different systems.
While virtual environments for Python, such as [`venv`](https://docs.python.org/3/library/venv.html) or [`conda`](https://www.anaconda.com/download), create reproducible environments for Python packages, containers create reproducible environments for an entire operating system.
This allows the inclusion and management of non-Python software in a project, such as the `cdo` and `esgpull` tools used in this project.


### Installing Podman
[back to top](#initial-setup)
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
user@local:~$ podman machine init
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
user@local:~$ podman machine start
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
user@local:~$ podman info
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
user@local:~$ podman version
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
user@local:~$ ls -la ~/.config/containers/
total 8
drwxr-xr-x  5 <user>  staff  160 Apr 28 10:57 .
drwx------  8 <user>  staff  256 Apr 28 10:55 ..
drwxr-xr-x  3 <user>  staff   96 Apr 28 10:55 podman
-rw-r--r--  1 <user>  staff  440 Apr 28 10:57 podman-connections.json
-rw-r--r--  1 <user>  staff    0 Apr 28 10:57 podman-connections.json.lock
```

---

### Testing Podman
[back to top](#initial-setup)

Next, I followed the [Basic Setup and Use of Podman](https://github.com/containers/podman/blob/main/docs/tutorials/podman_tutorial.md) guide.
To start, I ran the sample `nginx` container, calling it `basic_httpd`.
```console
user@local:~$ podman run --name basic_httpd -d -p 8080:80/tcp docker.io/nginx
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
user@local:~$ podman ps -a
CONTAINER ID  IMAGE                           COMMAND               CREATED             STATUS             PORTS                 NAMES
774a97cf2828  docker.io/library/nginx:latest  nginx -g daemon o...  About a minute ago  Up About a minute  0.0.0.0:8080->80/tcp  basic_httpd
```
Adding the `-a` flag shows "all" containers, but that doesn't result in any different output than without it at this moment because I just have the one container.

Then, I can inspect that running container.
```console
user@local:~$ podman inspect basic_httpd | grep IPAddress
               "IPAddress": "10.88.0.3",
                         "IPAddress": "10.88.0.3",
```
This is different than what is shown in the guide which says:
> "As the container is running in rootless mode, an IP address is not assigned and the value will be listed as 'none' in the output from inspect." 

<!-- So, I'm not sure if I am running rootless or not as I did, in fact, get an IP address. -->

Next, I tested the `httpd` server to make sure it is running on the expected port, displaying the index page.
```console
user@local:~$ curl http://localhost:8080
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
user@local:~$ podman logs 774a97cf2828
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
user@local:~$ podman top 774a97cf2828
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
user@local:~$ podman exec basic_httpd whoami
root
```
So, the container is running as `root`. 
Next, I'll see who owns the process.
```console
user@local:~$ podman top basic_httpd user huser
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
user@local:~$ podman stop basic_httpd
basic_httpd
```
Then, I'll remove this container and check to make sure it is gone.
```console
user@local:~$ podman rm basic_httpd
basic_httpd
user@local:~$ podman ps -a
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES
```

---

### Pod Manager extension for VSCodium
[back to top](#initial-setup)

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
This is the image that was built when [Testing Podman](#testing-podman).

Containers get added to the list in the Pod Manager sidebar when they start running. 
I can start the `basic_httpd` container again.
```console
user@local:seaicecp$ podman run --name basic_httpd -d -p 8080:80/tcp docker.io/nginx
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
user@local:seaicecp$ podman exec -it 9ab04fb2f7c0 /bin/sh
# basic_httpd whoami
root
# 
```
Then, to clean up, I will stop and remove this `basic_httpd` from outside the container.
```console
user@local:~$ podman stop basic_httpd
basic_httpd
user@local:~$ podman rm basic_httpd
basic_httpd
user@local:~$ podman ps -a
CONTAINER ID  IMAGE       COMMAND     CREATED     STATUS      PORTS       NAMES
```
If any terminals had been left open inside the container, they will have automatically exited when the container is removed.

---

### Building a simple container
[back to top](#initial-setup)

Above, I downloaded an existing image `docker.io/nginx` from a repository. 
For this project, I want to define my own.
The setup of a container is defined by a scripted that is named `Containerfile` with no file extension. 
A good way to start a container is to load an existing minimal distribution.
I chose the `trixie-slim` version of Debian as it is lightweight and [uses Python 3.13 by default](https://packages.debian.org/trixie/python3).

In [Py-Pkgs Chapter 2](https://py-pkgs.org/02-setup), they suggest using Miniconda to create an environment and the [`poetry`](https://python-poetry.org/) package to manage dependencies. 
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
user@local:seaicecp$ podman build -f Containerfile -t test_trixie .
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
user@local:seaicecp$ podman run -it --rm --name container_name test_trixie
root@<container_id>:/workspace# 
```
Where `<container_id>` is a 12-digit identifier of the container. 
While this container is running, I can hit the refresh button in the Pod Manager sidebar to see that there is a new container named `container_name`.
I can also verify that Python and `uv` are installed inside the container.
```console
root@<container_id>:/workspace# python
Python 3.13.5 (main, May  5 2026, 21:05:52) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
root@<container_id>:/workspace# uv --version
uv 0.11.17 (x86_64-unknown-linux-musl)
root@<container_id>:/workspace#
```
When I am done, I can exit the container.
```console
root@<container_id>:/workspace# exit
exit
user@local:seaicecp$ 
```
Upon exiting the container, I can refresh the Pod Manager sidebar again to see that the container removed itself upon exit because of the `--rm` flag.
This is important to keep from building up a large number of idle containers when starting a particular image many times.

With this working, the next step is to build out the `Containerfile` to set up the development environment with all the necessary packages, tools, and data access.

---


### The `Containerfile`
[back to top](#initial-setup)

Below is the current `Containerfile` used to build the image for this project.

```{literalinclude} ../../.devcontainer/Containerfile
:language: dockerfile
```

Note that this is meant to be executed via [the `start_container.sh` script](#the-start_container-script).
However, if testing a new build, it can be useful to pipe the output of `podman build` to a log file using `tee`.
```console
user@local:seaicecp$ podman build -f .devcontainer/Containerfile -t <image_name> . | tee .devcontainer/<log_file_name>.log
```

I'll explain each section of the `Containerfile` in detail below.


#### Pinning the versions of `uv` and `trixie-slim`
[back to top](#initial-setup)

For reproducibility purposes, I decided to pin the exact versions of `uv` and `trixie-slim` that my container uses. 
After [Building a simple container](#building-a-simple-container), I now see the following images in the Pod Manger sidebar:
- `ghcr.io/astral-sh/uv:latest`
- `docker.io/library/debian:trixie-slim`

I can get the exact hashes of the versions of `uv` and `trixie-slim` from their manifests.
```console
user@local:seaicecp$ podman image inspect debian:trixie-slim --format '{{.Digest}}'
sha256:e18da95f66066b7c5fa31491b524e83121271eca59a3d140f4906c8d0a090367
user@local:seaicecp$ podman image inspect ghcr.io/astral-sh/uv --format '{{.Digest}}'
sha256:5cbec7ab7753a6c763c6dda6a38f085c8c585ec9f53cfb4e7368b79ca30bc881
```


#### Defining environment variables
[back to top](#initial-setup)

The `Containerfile` defines a few environment variables to facilitate building the image.
- `DEBIAN_FRONTEND=noninteractive`
    - According to the askUbuntu post [DEBIAN_FRONTEND environment variable](https://askubuntu.com/questions/972516/debian-frontend-environment-variable), this prevents installations from getting stuck on interactive processes, such as when the user is asked to confirm or select something.
- `ENV UV_PROJECT_ENVIRONMENT=/workspace/.cvenv`
    - According to the Python Developer Tooling Handbook on [How to customize uv's virtual environment location](https://pydevtools.com/handbook/how-to/how-to-customize-uvs-virtual-environment-location/), this renames the default directory for the `uv` virtual environment from `.venv` to `.cvenv` to avoid conflicts with using the environment inside vs. outside the container.
    - Note that the use of the directory `/workspace` is [detailed below](#preparing-python-uv-and-the-working-directory).
- `ENV UV_LINK_MODE=copy`
    - According to the Python Developer Tooling Handbook on [How to use `uv` in a Dockerfile](https://pydevtools.com/handbook/how-to/how-to-use-uv-in-a-dockerfile/), this "tells uv to copy files instead of hard-linking them. When using Docker cache mounts, the cache and the target directory live on separate filesystems, so uv falls back to copying anyway. Setting this explicitly avoids the warning message."


#### Installing system and scientific dependencies
[back to top](#initial-setup)

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
- `chromium`
    - For taking "screenshots" of `html` maps to produce `.png` images.
- `chromium-driver`
    - For taking "screenshots" of `html` maps to produce `.png` images.
- `fonts-liberation`


#### Preparing Python, `uv`, and the working directory
[back to top](#initial-setup)

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


#### `uv` dependencies and Jupyter kernel
[back to top](#initial-setup)

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


#### Downloading commonly used Natural Earth 
[back to top](#initial-setup)

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


#### Setting up `esgpull` install
[back to top](#initial-setup)

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

The `.devcontainer/esgpull_entrypoint.sh` script assumes that the directory in which the data on the external volume is stored has been defined as `/seaicecp_data`, something which is set when executing the `podman run` command (see [The `start_container` script](#the-start_container-script)).
For more information on `esgpull`, see [Initializing `esgpull`](#initializing-esgpull).


#### Setting up the Jupyter server
[back to top](#initial-setup)

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


### The `start_container` script
[back to top](#initial-setup)

[The `Containerfile`](#the-containerfile) defines how the image for this project should be built.
I created a script called `start_container.sh` which ultimately starts the container from that image, but first checks to make sure the Podman virtual machine is running and whether the image exists already.
The script is shown below:

```{literalinclude} ../../start_container.sh
:language: bash
```

This script can be run with a simple `bash` command.
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
The output that continues to appear in this terminal as the Jupyter server is being used can be very helpful in debugging Jupyter-related issues.
The instructions above on how to start the container are also shown on the {doc}`Starting the Container <start_container>` page.

I'll explain each section of the `start_container.sh` script in detail below.


#### Set the script to fail on common errors
[back to top](#initial-setup)

The first line is `set -euo pipefail`. 
The GitHub Gist by `akrasic` called [`bash_strict_mode`](https://gist.github.com/akrasic/380bda362e0420be08709152c91ca1f9) explains that the `set` command is used to cause a script to fail very explicitly when encountering errors. 
This can be helpful to track down where exactly the bugs are, especially if the script calls other scripts. 


#### Ensure the virtual machine is running
[back to top](#initial-setup)

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


#### Set the parameters
[back to top](#initial-setup)

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


#### Check existing containers and images
[back to top](#initial-setup)

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


#### Set up access to external volumes
[back to top](#initial-setup)

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
user@local:seaicecp$ podman machine stop
Machine "podman-machine-default" stopped successfully
user@local:seaicecp$ podman machine rm
The following files will be deleted:


/Users/<user>/.config/containers/podman/machine/applehv/podman-machine-default.json
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default.sock
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default-gvproxy.sock
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default-api.sock
/var/folders/30/czkm3xpn6fx2v22bz_r2g37r0000gp/T/podman/podman-machine-default.log
Are you sure you want to continue? [y/N] y
```


#### Create the list of volumes
[back to top](#initial-setup)

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


#### Run the container
[back to top](#initial-setup)

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
The arguments of the command are, similar to [Building a simple container](#building-a-simple-container) (see the [Podman run docs](https://docs.podman.io/en/latest/markdown/podman-run.1.html) for details):
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


### Testing the container
[back to top](#initial-setup)

With the container running, I can test to make sure things were installed correctly. 
First, I'll check the versions of various packages, starting with `uv`.
```console
user@local:seaicecp$ podman exec -it <container_id> /bin/sh
# bash
root@<container_id>:/workspace# uv --version
uv 0.11.8 (x86_64-unknown-linux-musl)
```
Next, I'll check `cdo`.
```console
root@<container_id>:/workspace# cdo --version
Climate Data Operators version 2.5.1 (https://mpimet.mpg.de/cdo)
System: x86_64-pc-linux-gnu
CXX Compiler: g++ -std=gnu++20 -g -O2 -ffile-prefix-map=/build/reproducible-path/cdo-2.5.1=. -fstack-protector-strong -fstack-clash-protection -Wformat -Werror=format-security -fcf-protection -fopenmp -pthread
CXX version : g++ (Debian 14.2.0-19) 14.2.0
CXX library :
C Compiler: gcc -g -O2 -Werror=implicit-function-declaration -ffile-prefix-map=/build/reproducible-path/cdo-2.5.1=. -fstack-protector-strong -fstack-clash-protection -Wformat -Werror=format-security -fcf-protection -Wall -pedantic -fPIC -fopenmp -pthread -pthread
C version : gcc (Debian 14.2.0-19) 14.2.0
F77 Compiler: f77 -g -O2 -ffile-prefix-map=/build/reproducible-path/cdo-2.5.1=. -fstack-protector-strong -fstack-clash-protection -fcf-protection
F77 version : GNU Fortran (Debian 14.2.0-19) 14.2.0
Features: 1GB 4threads c++20 OpenMP45 Fortran pthreads HDF5 NC4/HDF5/threadsafe OPeNDAP sz udunits2 proj xml2 magics curl fftw3 hirlam_extensions sse2
Libraries: yac/3.4.0 NetCDF/4.9.3 HDF5/1.14.5 proj/9.6.0 xml2/2.9.14 curl/8.14.1(h8.13.0-rc3) magics/4.15.5
CDI data types: SizeType=size_t
CDI file types: srv ext ieg grb1 grb2 nc1 nc2 nc4 nc4c nc5 nczarr 
     CDI library version : 2.5.1
 ecCodes library version : 2.41.0
  NetCDF library version : 4.9.3 of Feb 14 2025 11:24:29 $
    exse library version : 2.0.0
    FILE library version : 1.9.1
```
To check `nco`, I'll check the version of `ncks` (NetCDF Kitchen Sink).
```console
root@<container_id>:/workspace# ncks --version
NCO netCDF Operators version 5.3.3 "Sea Shanty" built by sbuild on sbuild at Mar 29 2025 05:28:49
ncks version 5.3.3
```
Then, I can check Python.
```console
root@<container_id>:/workspace# python
Python 3.13.5 (main, Jun 25 2025, 18:55:22) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
```


### Cleaning up old images
[back to top](#initial-setup)

During the testing above, several images were generated.
In the Pod Manager sidebar, under the "Overview" dropdown, a summary of the images can be seen.
Usually, you will need to hit the refresh button next to this dropdown to see any information.
For the images, containers, and local volumes, it lists the total number, the number active, the disk space used, and the reclaimable disk space.

When testing out new builds of the `Containerfile`, it is easy to generate many images.
Podman can list the existing images. 
```console
user@local:seaicecp$ podman images -a
REPOSITORY                TAG          IMAGE ID      CREATED      SIZE
<none>                    <none>       55b854bc8dcd  2 days ago   199 MB
localhost/test_trixie     latest       7bab3cfc2aa3  2 days ago   199 MB
<none>                    <none>       b907eed1ae8b  2 days ago   199 MB
<none>                    <none>       6dd8a6c94600  2 days ago   142 MB
<none>                    <none>       4f123f8d89fe  2 days ago   142 MB
<none>                    <none>       5808b4b9aad3  2 days ago   81.1 MB
ghcr.io/astral-sh/uv      latest       b960411dc937  6 days ago   58.2 MB
docker.io/library/nginx   latest       7aaca76c508f  12 days ago  165 MB
docker.io/library/debian  trixie-slim  f283d70f8784  2 weeks ago  81.1 MB
localhost/seaicecp_7      latest       b05b6acdb72b  3 weeks ago  2.78 GB
```
While the image for this project is a reasonable 2.78 GB, it adds up quickly when there are dozens of copies.
Podman provides an easy `prune` command to clean this up. 
When this command is run, it will remove all images that do not have an associated container that is currently running. 
This makes it convenient as I can just start a container from the image that I want to keep then, from outside that container, run a `prune` command.
```console
user@local:seaicecp$ podman image prune -a
WARNING! This command removes all images without at least one container associated with them.
Are you sure you want to continue? [y/N] y
7aaca76c508f7d121ff29cbe9dd071012486d00c21e17655eb1a1dfb711e9330
b960411dc937f9b4d9762349f5f77772d36dead003baa3bc01330abe8e1f38a6
f283d70f878433b889e4b9252110fad858e0e0887df5bac91cd2ad4ccb2b3a2a
5808b4b9aad30e55a565efe96b48bb0628439d44dc31883d7be8b24998e52bfd
4f123f8d89feb6111a63528bf05c56cb2831684cda3ef4b7e2cad3c87d567a58
6dd8a6c94600c177a0a4a6f0166574c35d720766c981bbd10f34d77be956f0bc
b907eed1ae8b4ec83fe12df4292630c67ca77d99f5e966dfa0e99e8077d2bae7
55b854bc8dcd53e9a5d01887214276422374802dd565dd165b3b78af8af79f18
7bab3cfc2aa34bf43d9a63ccb8428a859c9f64a807186a4262b17bc5ffe0b4eb
```
I can then confirm that only one image remains.
```console
user@local:seaicecp$ podman images -a
REPOSITORY            TAG         IMAGE ID      CREATED      SIZE
localhost/seaicecp_7  latest      b05b6acdb72b  3 weeks ago  2.78 GB
```


## Virtual environment and packages
[back to top](#initial-setup)


### Activating the virtual environment
[back to top](#initial-setup)

When initializing the project, `uv` automatically creates a virtual environment in `.venv/`.
That environment can be used outside the container. 
In the section [Defining environment variables](#defining-environment-variables), I noted that I changed the default virtual environment location for `uv` to be `.cvenv` inside the container.
I can easily activate it by first starting a terminal inside the container.
```console
podman exec -it <container_id> /bin/sh

The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
user@local:seaicecp$ podman exec -it <container_id> /bin/sh
# 
```
Then, I activate `bash` and source the virtual environment directory.
```console
# bash
root@<container_id>:/workspace# source .cvenv/bin/activate
(seaicecp) root@<container_id>:/workspace# 
```
Note that the virtual environment's name `(seaicecp)` is now at the beginning of the command prompt.


### Adding package dependencies
[back to top](#initial-setup)

Using `uv` to add dependencies works similarly to `poetry` as described in [Py-Pkgs 3.6. Adding dependencies to your package](https://py-pkgs.org/03-how-to-package-a-python). 
When a `uv add <package>` command is run, that package is automatically added to [the `pyproject.toml` file](#the-pyprojecttoml-file).
See `uv` docs for [The project environment](https://docs.astral.sh/uv/concepts/projects/layout/#the-project-environment) for more information.


#### Packages for datasets
[back to top](#initial-setup)

I use `xarray` as the main workhorse to handle datasets.
```console
(seaicecp) root@<container_id>:/workspace# uv add xarray
Resolved 48 packages in 343ms
Prepared 1 package in 318ms
Installed 1 package in 11ms
 + xarray==2026.4.0
```
In order to load data from NetCDF files into an `xarray` dataset, I also need to add the `netcdf4` package.
```console
(seaicecp) root@<container_id>:/workspace# uv add netcdf4
Resolved 78 packages in 716ms
Prepared 2 packages in 3.74s
Installed 2 packages in 13ms
 + cftime==1.6.5
 + netcdf4==1.7.4
```
I also specifically added `dask` so that I can take advantage of lazy loading with `xarray.open_dataset()`. 
This allows me to filter a large dataset before actually loading the entire file into memory.
```console
(seaicecp) root@<container_id>:/workspace# uv add dask
Resolved 198 packages in 708ms
      Built seaicecp @ file:///workspace
Prepared 1 package in 18ms
Uninstalled 1 package in 13ms
Installed 7 packages in 2.48s
 + cloudpickle==3.1.2
 + dask==2026.3.0
 + fsspec==2026.4.0
 + locket==1.0.0
 + partd==1.4.2
 ~ seaicecp==0.1.0 (from file:///workspace)
 + toolz==1.1.0
```


#### Packages for making plots
[back to top](#initial-setup)

For plots, I added the `hvplot` package to be able to make `html` maps of irregular gridded data without interpolating onto a regular grid first.
```console
(seaicecp) root@<container_id>:/workspace# uv add hvplot
Resolved 170 packages in 2.70s
      Built seaicecp @ file:///workspace
Prepared 16 packages in 6.01s
Uninstalled 1 package in 14ms
Installed 16 packages in 18.01s
 + bokeh==3.9.0
 + colorcet==3.2.1
 + contourpy==1.3.3
 + holoviews==1.22.1
 + hvplot==0.12.2
 + linkify-it-py==2.1.0
 + markdown==3.10.2
 + narwhals==2.20.0
 + panel==1.8.10
 + param==2.3.3
 + pillow==12.2.0
 + pyviz-comms==3.0.6
 ~ seaicecp==0.1.0 (from file:///workspace)
 + tqdm==4.67.3
 + uc-micro-py==2.0.0
 + xyzservices==2026.3.0
```
Then, I added `cartopy` to have access to map projections through the submodule `cartopy.crs`.
```console
(seaicecp) root@<container_id>:/workspace# uv add cartopy
Resolved 178 packages in 1.40s
      Built seaicecp @ file:///workspace
Prepared 9 packages in 6.54s
Uninstalled 1 package in 10ms
Installed 9 packages in 5.07s
 + cartopy==0.25.0
 + cycler==0.12.1
 + fonttools==4.62.1
 + kiwisolver==1.5.0
 + matplotlib==3.10.9
 + pyproj==3.7.2
 + pyshp==3.0.3
 ~ seaicecp==0.1.0 (from file:///workspace)
 + shapely==2.1.2
```
I also added the `geoviews` package for handling physical features on maps.
```console
(seaicecp) root@<container_id>:/workspace# uv add geoviews
Resolved 179 packages in 643ms
      Built seaicecp @ file:///workspace
Prepared 2 packages in 503ms
Uninstalled 1 package in 13ms
Installed 2 packages in 859ms
 + geoviews==1.15.1
 ~ seaicecp==0.1.0 (from file:///workspace)
```
When tyring to plot data from the HadGEM3-GC models over time, I got the following error.
```console
ImportError: Plotting of arrays of cftime.datetime objects or arrays indexed by cftime.datetime objects requires the optional `nc-time-axis` (v1.2.0 or later) package.
```
It turns out that these models use the type `cftime.Datetime360Day` instead of `numpy.datetime64`, which causes issues for `matplotlib` when using time values on one of the axes.
In the GitHub issue [How to convert cftime.Datetime360Day() object to python datetime?](https://github.com/Unidata/cftime/issues/111), one of the maintainers of `xarray` mentioned that:
> "We [fixed this very recently](https://github.com/pydata/xarray/pull/2665) in xarray by adding an optional dependency on [nc-time-axis](https://github.com/SciTools/nc-time-axis), a package that enables plotting cftime dates in matplotlib. The changes will take effect in the next version, which has yet to be released (version 0.12.0)."

Adding `nc-time-axis` indeed fixed the issue. 
```console
(seaicecp) root@<container_id>:/workspace# uv add nc-time-axis
Resolved 200 packages in 697ms
      Built seaicecp @ file:///workspace
Prepared 2 packages in 174ms
Uninstalled 1 package in 20ms
Installed 2 packages in 139ms
 + nc-time-axis==1.4.1
 ~ seaicecp==0.1.0 (from file:///workspace)
```
I had also tried to use [`xarray.convert_calendar()`](https://docs.xarray.dev/en/stable/generated/xarray.Dataset.convert_calendar.html) instead of installing `nc-time-axis`, but with no luck. 
They have notes in the documentation about how to deal with "360_day" calendars.
However, I still found that some dates being dropped or set to the missing value, even though all the dates are the 16th of each month.
I'm sticking with just using `nc-time-axis` as my solution.


#### Packages for saving plots
[back to top](#initial-setup)

The `html` plots that are made with `hvplot` cannot be directly saved to a `png` file. 
As a workaround, I added the packages `chromium` and `chromium-driver` to [the `Containerfile`](#the-containerfile) in order to open an `html` plot in a browser within the container, take a "screenshot", and save that as a `png` image.
In order for that process to work, I added the `selenium` and `bokeh` packages.
```console
(seaicecp) root@<container_id>:/workspace# uv add selenium
Resolved 187 packages in 910ms
      Built seaicecp @ file:///workspace
Prepared 9 packages in 1.64s
Uninstalled 1 package in 31ms
Installed 9 packages in 2.54s
 + outcome==1.3.0.post0
 + pysocks==1.7.1
 ~ seaicecp==0.1.0 (from file:///workspace)
 + selenium==4.43.0
 + sniffio==1.3.1
 + sortedcontainers==2.4.0
 + trio==0.33.0
 + trio-websocket==0.12.2
 + wsproto==1.3.2
(seaicecp) root@<container_id>:/workspace# uv add bokeh
Resolved 187 packages in 323ms
      Built seaicecp @ file:///workspace
Prepared 1 package in 18ms
Uninstalled 1 package in 14ms
Installed 1 package in 45ms
 ~ seaicecp==0.1.0 (from file:///workspace)
```
I also added the `pillow` package for additional `png` manipulation tools.
```console
(seaicecp) root@<container_id>:/workspace# uv add pillow
Resolved 187 packages in 331ms
      Built seaicecp @ file:///workspace
Prepared 1 package in 20ms
Uninstalled 1 package in 14ms
Installed 1 package in 60ms
 ~ seaicecp==0.1.0 (from file:///workspace)
```


#### Packages for Jupyter notebooks
[back to top](#initial-setup)

In order to use Jupyter notebooks with the `.cvenv` virtual environment, I added `ipykernel` and `jupyter`.
```console
(seaicecp) root@<container_id>:/workspace# uv add ipykernel jupyter
Resolved 134 packages in 1.15s
      Built seaicecp @ file:///workspace
Prepared 51 packages in 3.38s
Uninstalled 1 package in 19ms
Installed 51 packages in 14.63s
 + anyio==4.13.0
 + argon2-cffi==25.1.0
 + argon2-cffi-bindings==25.1.0
 + arrow==1.4.0
 + async-lru==2.3.0
 + beautifulsoup4==4.14.3
 + bleach==6.3.0
 + cffi==2.0.0
 + defusedxml==0.7.1
 + fqdn==1.5.1
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + ipywidgets==8.1.8
 + isoduration==20.11.0
 + json5==0.14.0
 + jsonpointer==3.1.1
 + jupyter==1.1.1
 + jupyter-console==6.6.3
 + jupyter-events==0.12.1
 + jupyter-lsp==2.3.1
 + jupyter-server==2.17.0
 + jupyter-server-terminals==0.5.4
 + jupyterlab==4.5.6
 + jupyterlab-pygments==0.3.0
 + jupyterlab-server==2.28.0
 + jupyterlab-widgets==3.0.16
 + lark==1.3.1
 + mistune==3.2.0
 + nbconvert==7.17.1
 + notebook==7.5.5
 + notebook-shim==0.2.4
 + pandocfilters==1.5.1
 + prometheus-client==0.25.0
 + pycparser==3.0
 + python-json-logger==4.1.0
 + rfc3339-validator==0.1.4
 + rfc3986-validator==0.1.1
 + rfc3987-syntax==1.1.0
 ~ seaicecp==0.1.0 (from file:///workspace)
 + send2trash==2.1.0
 + setuptools==82.0.1
 + soupsieve==2.8.3
 + terminado==0.18.1
 + tinycss2==1.4.0
 + tzdata==2026.2
 + uri-template==1.3.0
 + webcolors==25.10.0
 + webencodings==0.5.1
 + websocket-client==1.9.0
 + widgetsnbextension==4.0.15
```


#### Packages for external tools
[back to top](#initial-setup)

I added the Python package for `cdo` to be able to call it's functions from Python scripts. 
Note that this requires that the `cdo` CLI is installed, which is done in the `Containerfile`.
```console
(seaicecp) root@<container_id>:/workspace# uv add cdo
Resolved 199 packages in 2.61s
      Built seaicecp @ file:///workspace
Prepared 2 packages in 177ms
Uninstalled 1 package in 17ms
Installed 2 packages in 68ms
 + cdo==1.6.1
 ~ seaicecp==0.1.0 (from file:///workspace)
(seaicecp) root@<container_id>:/workspace# python
Python 3.13.5 (main, Jun 25 2025, 18:55:22) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cdo
>>> print(cdo.__version__)
1.6.0
```
Next, I added the `esgpull` package to be able to download HighResMIP data.
On the [`esgpull` documentation Installation page](https://esgf.github.io/esgf-download/installation/) they show an example using `uv tool install` which creates an isolated installation.
However, I use `uv add` so that `esgpull` becomes a persistent dependency of the project.
I specify the source with `git+https://github.com/ESGF/esgf-download` in order to get the latest release of the package to resolve an issue I was encountering.
```console
root@<container_id>:/workspace# uv add git+https://github.com/ESGF/esgf-download
Resolved 198 packages in 1.07s
      Built seaicecp @ file:///workspace
    Updated https://github.com/ESGF/esgf-download (726ef1166114eadd085c24c6e1542ec0be052e03)
      Built esgpull @ git+https://github.com/ESGF/esgf-download@726ef1166114eadd085c24c6e1542ec0be052e03
Prepared 21 packages in 3.08s
Uninstalled 1 package in 13ms
Installed 21 packages in 2.54s
 + aiofiles==25.1.0
 + aiostream==0.7.1
 + alembic==1.18.4
 + annotated-types==0.7.0
 + cattrs==26.1.0
 + click-params==0.5.0
 + cryptography==48.0.0
 + deprecated==1.3.1
 + esgpull==0.9.6 (from git+https://github.com/ESGF/esgf-download@726ef1166114eadd085c24c6e1542ec0be052e03)
 + mako==1.3.12
 + pydantic==2.13.4
 + pydantic-core==2.46.4
 + pydantic-settings==2.14.0
 + pyopenssl==26.2.0
 + python-dotenv==1.2.2
 + rich==15.0.0
 ~ seaicecp==0.1.0 (from file:///workspace)
 + tomlkit==0.14.0
 + typing-inspection==0.4.2
 + validators==0.22.0
 + wrapt==2.1.2
```
The `esgpull` maintainer `svenrdz` replied to [the issue that I posted on the `esgpull` GitHub](https://github.com/ESGF/esgf-download/issues/148). 
He found a fix, which was to put in a short sleep timer before trying to make a new `httpx.AsyncClient`.
This fix can be seen in `.cvenv/lib/python3.13/site-packages/esgpull/context.py`:
```python
...
    async def _fetch_one(self, result: RT) -> RT:
        host = result.request.url.host
        semaphore = self.get_or_create_semaphore(host)

        # The bridge API tends to produce non-standard errors when too many
        # new connections open in a short time span. With no sleep, the 4th
        # connection is always where it breaks. 50ms sleep seems to fix that.
        if self.client is None:
            await asyncio.sleep(0.005)
...
```
This should be included in future updates to `esgpull` which should make it unnecessary to specify the exact commit when adding it with `uv` as shown above.

Using `esgpull` requires additional steps [as noted on the Installation page](https://esgf.github.io/esgf-download/installation/#setup).
I detail how I managed that set up in the [Initializing `esgpull`](#initializing-esgpull) section later in this guide.


#### Packages for testing
[back to top](#initial-setup)

In order to run tests, following [Py-Pkgs Section 3.7.2. Running tests](https://py-pkgs.org/03-how-to-package-a-python#running-tests) and [Py-Pkgs Section 3.7.3. Code coverage](https://py-pkgs.org/03-how-to-package-a-python#code-coverage), I installed `pytest` and `pytest-cov` as development dependencies by specifying the `--dev` group.
This means that, if someone where to install `seaicecp` as a package for their own purposes, the packages in the `--dev` group would not be installed by default.
```console
root@<container_id>:/workspace# uv add --dev pytest
Resolved 190 packages in 2.15s
      Built seaicecp @ file:///workspace
Prepared 4 packages in 210ms
Uninstalled 1 package in 14ms
Installed 4 packages in 499ms
 + iniconfig==2.3.0
 + pluggy==1.6.0
 + pytest==9.0.3
 ~ seaicecp==0.1.0 (from file:///workspace)
root@<container_id>:/workspace# uv add --dev pytest-cov
Resolved 192 packages in 512ms
      Built seaicecp @ file:///workspace
Prepared 3 packages in 181ms
Uninstalled 1 package in 16ms
Installed 3 packages in 337ms
 + coverage==7.13.5
 + pytest-cov==7.1.0
 ~ seaicecp==0.1.0 (from file:///workspace)
```
<!-- ```console
root@<container_id>:/workspace# uv add --dev debugpy   
Resolved 192 packages in 165ms
      Built seaicecp @ file:///workspace
Prepared 1 package in 20ms
Uninstalled 1 package in 14ms
Installed 1 package in 69ms
 ~ seaicecp==0.1.0 (from file:///workspace)
root@<container_id>:/workspace# 
``` -->


#### Packages for documentation
[back to top](#initial-setup)

Following [Py-Pkgs 3.8.4. Building documentation](https://py-pkgs.org/03-how-to-package-a-python#building-documentation), I added the packages necessary to build the documentation you are reading to the `--dev` group.
```console
(seaicecp) root@<container_id>:/workspace# uv add --dev myst-nb sphinx-autoapi sphinx-rtd-theme
Resolved 112 packages in 1.08s
      Built seaicecp @ file:///workspace
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
 ~ seaicecp==0.1.0 (from file:///workspace)
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


### The `pyproject.toml` file
[back to top](#initial-setup)

After adding all the above packages as dependencies, the `pyproject.toml` file now appears as below.
```{literalinclude} ../../pyproject.toml
:language: toml
```
When new packages are added to the project, they will be cached the next time the container is run.


### Building the package
[back to top](#initial-setup)

As shown in Astral's [Build systems](https://docs.astral.sh/uv/concepts/projects/config/#build-systems) documentation for `uv`, I had used the `--package` flag when [initializing the repository with `uv`](#using-uv-init). 
In Astral's [Building your package](https://docs.astral.sh/uv/guides/package/#building-your-package) section, I used the 

```console
user@local:seaicecp$ podman exec -it <container_id> /bin/sh
# bash 
root@<container_id>:/workspace# source .cvenv/bin/activate
(seaicecp) root@<container_id>:/workspace# uv sync
Resolved 200 packages in 550ms
      Built seaicecp @ file:///workspace
Prepared 1 package in 53ms
Installed 1 package in 12ms
 + seaicecp==0.1.0 (from file:///workspace)
(seaicecp) root@<container_id>:/workspace# uv lock
Resolved 200 packages in 21ms
```

```console
(seaicecp) root@<container_id>:/workspace# uv build
Building source distribution (uv build backend)...
Building wheel from source distribution (uv build backend)...
Successfully built dist/seaicecp-0.1.0.tar.gz
Successfully built dist/seaicecp-0.1.0-py3-none-any.whl
```



```console
(seaicecp) root@<container_id>:/workspace# uv version
seaicecp 0.1.0
```

I can now import the package in the Python interpreter.
```console
(seaicecp) root@<container_id>:/workspace# python
Python 3.13.5 (main, Jun 25 2025, 18:55:22) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import seaicecp
>>> print(seaicecp.__version__)
0.1.0
```


### Using a Jupyter notebook in the container
[back to top](#initial-setup)

Instructions on how to test whether you can access the Jupyter server inside the container are shown in the {doc}`Jupyter Notebook Test <jupyter_test>` guide.
Once that is working, I can test to see whether the Jupyter server has access to the `seaicecp` package by executing a cell with the following code.
```python
import seaicecp
print(seaicecp.__version__)
```
```
0.1.0
```


### Initializing `esgpull`
[back to top](#initial-setup)

Data from the CMIP6 HighResMIP models can be downloaded from the [ESGF Federated Nodes](https://esgf-node.ornl.gov/search) webportal, which has great search functionality but tedious manual downloading, or through Globus, which augments the webportal through an application you can install on your system.
However, I decided to use [`esgpull`](https://esgf.github.io/esgf-download/quickstart/) for this project, which offers a command line interface for searching and downloading.
For detailed reasoning on choosing `esgpull`, see the {doc}`Downloading model data with esgpull <../docs_data/esgpull_downloads>` guide. 


#### Creating an `esgpull` install
[back to top](#initial-setup)

In the section [Packages for external tools](#packages-for-external-tools), I added `esgpull` as a dependency for the Python environment. 
As noted in the [Installation page](https://esgf.github.io/esgf-download/installation/#setup) under "Setup," an additonal step must be taken before `esgpull` can be used, namely running the `esgpull self install` command.
> "The reason is that esgpull is prevented from writing anything on disk until installed.
> 
> Installing esgpull equates choosing a directory in which it is allowed to write anything it needs to run properly. It also creates all the required files/directories in that directory and fetches some metadata from ESGF that is required to run properly."

In the `esgpull_entrypoint.sh` script, (see [Setting up `esgpull` install](#setting-up-esgpull-install)), I run `uv run esgpull self install bergybits` from the directory where I want the data to be (in this case, `/seaice_data` which is connected to my external drive) to create an install called `bergybits`.

The first time this is run, the output will indicate that a new install has been created.
```console
(seaicecp) root@<container_id>:/workspace# cd /seaicecp_data/
(seaicecp) root@<container_id>:/seaicecp_data# uv run esgpull self install bergybits
──────────────────────────────────── esgpull installation ────────────────────────────────────
Creating install directory and files at /seaicecp_data/bergybits
Install config added to /root/.config/esgpull/installs.json
```
On subsequent times running the `start_container.sh` script, `esgpull` will automatically recognize and use the existing install that has been set up with whatever data has already been downloaded.
```console
...
───────────────────────────────── esgpull installation ─────────────────────────────────
Using existing install at /seaicecp_data/bergybits
Install config added to /root/.config/esgpull/installs.json
```

If no name for the install is given, (i.e., running just `uv run esgpull self install`), then you will be taken through an interactive setup process shown below where you can specify the name and location of the install.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull self install
──────────────────────────────────────────────────── esgpull installation ────────────────────────────────────────────────────
Install location (/workspace/.esgpull): .esgpull
Name (optional): new_install
Creating install directory and files at /workspace/.esgpull
Install config added to /root/.config/esgpull/installs.json
```
I can view all the installs I have setup where the one marked with `*` is the one that is currently selected.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull self choose
Install locations           
    /seaicecp_data/bergybits 
 *  /workspace/.esgpull     
```
I can choose a different install by specifying the name at the end of that command.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull self choose /seaicecp_data/bergybits/
(seaicecp) root@<container_id>:/workspace# uv run esgpull self choose
Install locations           
 *  /seaicecp_data/bergybits 
    /workspace/.esgpull     
```
To delete an install, select it first, then use the `esgpull self delete` command.
To remove the associated data, run the `rm` command suggested by the output.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull self choose /workspace/.esgpull/
(seaicecp) root@<container_id>:/workspace# uv run esgpull self choose
Install locations                 
    /seaicecp_data/bergybits      
 *  /workspace/.esgpull
(seaicecp) root@<container_id>:/workspace# uv run esgpull self delete
You are going to delete: /workspace/.esgpull
Please enter '.esgpull' to continue: .esgpull
Deleting /workspace/.esgpull from config...
To remove all files from this install, run:

$ rm -rf /workspace/.esgpull
(seaicecp) root@<container_id>:/workspace# rm -rf /workspace/.esgpull/
(seaicecp) root@<container_id>:/workspace# 
```


#### Configuring the `esgpull` install
[back to top](#initial-setup)

The first time I tried to search with `esgpull`, I got the following error.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull search
(
    'fetch',
    [
        HTTPStatusError("Server error '500 500' for url 
'https://esgf-node.ipsl.upmc.fr/esg-search/search?type=File&offset=0&limit=0&format=applicatio
n%2Fsolr%2Bjson&fields=instance_id&distrib=true&latest=true&replica=true&retracted=false'\nFor
 more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500")
    ]
)
ERROR 'esgf-node.ipsl.upmc.fr' is not responding
Aborted!
```
This clearly indicates that the French node is not responding currently.
However, in an older version of `esgpull`, the error was more cryptic.
<details>

<summary>Expand for an older version of the error message</summary>

```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull search
[2026-04-14 18:33:45]  ERROR     root

  + Exception Group Traceback (most recent call last):
  ...
    |     raise HTTPStatusError(message, request=request, response=self)
    | httpx.HTTPStatusError: Server error '500 500' for url 'https://esgf-node.ipsl.upmc.fr/esg-search/search?type=File&offset=0&limit=0&format=application%2Fsolr%2Bjson&fields=instance_id&distrib=true&latest=true&retracted=false'
    | For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
    +------------------------------------
ExceptionGroup: fetch (1 sub-exception)
See /workspace/bergybits/log/esgpull-search-2026-04-14_22-33-44.log for error log.
Aborted!
```
The line with `Server error '500 500' for url 'https://esgf-node.ipsl.upmc.fr/...` led me to be confused as to why it would be checking a French web domain.

</details>

I checked the configuration for this `esgpull` install.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull config
──────────────────────────── /seaicecp_data/bergybits/config.toml ────────────────────────────
[paths]
data = "/seaicecp_data/bergybits/data"
db = "/seaicecp_data/bergybits/db"
log = "/seaicecp_data/bergybits/log"
tmp = "/seaicecp_data/bergybits/tmp"
plugins = "/seaicecp_data/bergybits/plugins"

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
This confirms install I created has `index_node = "esgf-node.ipsl.upmc.fr"`.
I can check the status of the available nodes.
This information should also be available at the [ESGF Nodes Status Summary page](https://metagrid.esgf-west.org/nodes/), however that site is currently not working.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull index-nodes
                node                │   status    
════════════════════════════════════╪═════════════
 esgf-node.ornl.gov/esgf-1-5-bridge │          OK 
                           us-index │ no response 
                    esgf.ceda.ac.uk │          OK 
                    esgf.nci.org.au │ no response 
             esgf-node.ipsl.upmc.fr │ no response 
                  esgf-data.dkrz.de │          OK
```
And here's the problem.
The French node is indeed not responding.
I changed the index node to be the one recommended for the USA region.
```console
(workspace) root@<container_id>:/seaicecp_data# uv run esgpull config api.index_node esgf-node.ornl.gov/esgf-1-5-bridge
[api]
index_node = "esgf-node.ornl.gov/esgf-1-5-bridge"

👍 New config file created at /seaicecp_data/bergybits/config.toml.
```

Then, I was able to perform a search:
```console
(workspace) root@<container_id>:/workspace# uv run esgpull search project:CMIP6 activity_id:HighResMIP
Found 66629 datasets.
 id │                                 dataset                                 │ #  │    size     │     data_node      
════╪═════════════════════════════════════════════════════════════════════════╪════╪═════════════╪════════════════════
  0 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.control-1950.r1i1p1f1.CFmon.clt… │ 10 │     2.9 GiB │ esgf-data.ucar.edu 
  1 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.control-1950.r1i1p1f1.Lmon.mrro… │ 10 │ 1,002.9 MiB │ esgf-data.ucar.edu 
  2 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.control-1950.r1i1p1f1.Lmon.tsl.… │ 10 │     9.9 GiB │ esgf-node.ornl.gov 
  3 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.control-1950.r1i1p1f1.Omon.soga… │ 99 │     2.8 MiB │ esgf-node.ornl.gov 
  4 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Amon.ta… │  1 │   719.4 MiB │ esgf-data.ucar.edu 
  5 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Amon.ta… │  1 │   738.9 MiB │ esgf-node.ornl.gov 
  6 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Amon.ta… │  1 │   752.3 MiB │ esgf-node.ornl.gov 
  7 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.CFmon.c… │  1 │    36.0 GiB │ esgf-data.ucar.edu 
  8 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.CFmon.c… │  1 │   980.0 MiB │ esgf-node.ornl.gov 
  9 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.CFmon.c… │  1 │   964.7 MiB │ esgf-data.ucar.edu 
 10 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.CFmon.p… │  1 │   985.8 MiB │ esgf-data.ucar.edu 
 11 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.CFmon.p… │  1 │   985.8 MiB │ esgf-node.ornl.gov 
 12 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Emon.mr… │  1 │     3.2 GiB │ eagle.alcf.anl.gov 
 13 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Emon.ps… │  1 │   711.3 MiB │ eagle.alcf.anl.gov 
 14 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Lmon.mr… │  1 │   324.7 MiB │ eagle.alcf.anl.gov 
 15 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Lmon.tr… │  1 │   310.3 MiB │ esgf-node.ornl.gov 
 16 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Omon.so… │ 36 │     1.0 MiB │ esgf-node.ornl.gov 
 17 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.Omon.to… │ 36 │     1.0 MiB │ esgf-data.ucar.edu 
 18 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.SImon.s… │  1 │    59.9 kiB │ eagle.alcf.anl.gov 
 19 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-future.r1i1p1f1.SImon.s… │  1 │     1.6 GiB │ eagle.alcf.anl.gov
```

I also set the `replica` option to `true`.
```console
(workspace) root@<container_id>:/workspace# uv run esgpull config api.default_options.replica true
[api.default_options]
replica = "true"

Previous value: none
```
I'm not certain this step is strictly necessary, but it works.
Here is what the configuration for my `esgpull` install looks like.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull config
──────────────────────────── /seaicecp_data/bergybits/config.toml ────────────────────────────
[paths]
data = "/seaicecp_data/bergybits/data"
db = "/seaicecp_data/bergybits/db"
log = "/seaicecp_data/bergybits/log"
tmp = "/seaicecp_data/bergybits/tmp"
plugins = "/seaicecp_data/bergybits/plugins"

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
replica = "true"
retracted = "false"

[plugins]
enabled = false
```


## Documentation
[back to top](#initial-setup)


### Building documentation
[back to top](#initial-setup)

In the section, [Packages for documentation](#packages-for-documentation), I added the `myst-nb` `sphinx-autoapi` and `sphinx-rtd-theme` packages to the development group of the project. 
To build the documentation, activate the virtual environment, go into the `docs/` directory, and run the `make` command.
This will produce a lot of output, especially the first time running, so I have hidden most of it.
```console
(seaicecp) root@<container_id>:/workspace# cd docs
(seaicecp) root@<container_id>:/workspace/docs# make html
Running Sphinx v9.1.0
loading translations [en]... done
loading pickled environment... The configuration has changed (3 options: 'html_permalinks_icon', 'jquery_use_sri', 'mathjax3_config')
done
...
```

<details>

<summary>Expand for more output.</summary>

```console
...
myst v5.0.0: MdParserConfig(commonmark_only=False, gfm_only=False, enable_extensions={'amsmath', 'dollarmath'}, disable_syntax=[], all_links_external=False, links_external_new_tab=False, url_schemes=('http', 'https', 'wiki', 'doi', 'gh-issue'), ref_domains=None, fence_as_directive=set(), number_code_blocks=[], title_to_header=False, heading_anchors=0, heading_slug_func=None, html_meta={}, footnote_sort=True, footnote_transition=True, words_per_minute=200, substitutions={}, linkify_fuzzy_links=True, dmath_allow_labels=True, dmath_allow_space=True, dmath_allow_digits=True, dmath_double_inline=False, update_mathjax=True, mathjax_classes='tex2jax_process|mathjax_process|math|output_area', enable_checkboxes=False, suppress_warnings=[], highlight_code_blocks=True)
myst-nb v1.4.0: NbParserConfig(custom_formats={}, metadata_key='mystnb', cell_metadata_key='mystnb', kernel_rgx_aliases={}, eval_name_regex='^[a-zA-Z_][a-zA-Z0-9_]*$', execution_mode='auto', execution_cache_path='', execution_excludepatterns=(), execution_timeout=30, execution_in_temp=False, execution_allow_errors=False, execution_raise_on_error=False, execution_show_tb=False, merge_streams=False, render_plugin='default', remove_code_source=False, remove_code_outputs=False, scroll_outputs=False, code_prompt_show='Show code cell {type}', code_prompt_hide='Hide code cell {type}', number_source_lines=False, output_stderr='show', render_text_lexer='myst-ansi', render_error_lexer='ipythontb', render_image_options={}, render_figure_options={}, render_markdown_format='commonmark', output_folder='build', append_css=True, metadata_to_fm=False)
Using jupyter-cache at: /workspace/docs/_build/.jupyter_cache
[AutoAPI] Reading files... [100%] /workspace/src/seaicecp/params/var_params.py
[AutoAPI] Mapping Data... [100%] /workspace/src/seaicecp/params/var_params.py
[AutoAPI] Rendering Data... [  4%] seaicecp
[AutoAPI] Rendering Data... [  7%] seaicecp.plot
[AutoAPI] Rendering Data... [ 11%] seaicecp.path
[AutoAPI] Rendering Data... [ 15%] seaicecp.verify
[AutoAPI] Rendering Data... [ 19%] seaicecp.params
[AutoAPI] Rendering Data... [ 22%] seaicecp.dataset
[AutoAPI] Rendering Data... [ 26%] seaicecp.seaicecp
[AutoAPI] Rendering Data... [ 30%] seaicecp.dataset.tmp
[AutoAPI] Rendering Data... [ 33%] seaicecp.plot.hvplots
[AutoAPI] Rendering Data... [ 37%] seaicecp.path.file_lists
[AutoAPI] Rendering Data... [ 41%] seaicecp.plot.time_series
[AutoAPI] Rendering Data... [ 44%] seaicecp.path.model_paths
[AutoAPI] Rendering Data... [ 48%] seaicecp.plot.save_hvplots
[AutoAPI] Rendering Data... [ 52%] seaicecp.plot.limit_extent
[AutoAPI] Rendering Data... [ 56%] seaicecp.dataset.date_type
[AutoAPI] Rendering Data... [ 59%] seaicecp.dataset.grid_type
[AutoAPI] Rendering Data... [ 63%] seaicecp.params.var_params
[AutoAPI] Rendering Data... [ 67%] seaicecp.verify.verify_path
[AutoAPI] Rendering Data... [ 70%] seaicecp.dataset.field_mean
[AutoAPI] Rendering Data... [ 74%] seaicecp.plot.seasonal_cycle
[AutoAPI] Rendering Data... [ 78%] seaicecp.path.variable_paths
[AutoAPI] Rendering Data... [ 81%] seaicecp.dataset.get_variable
[AutoAPI] Rendering Data... [ 85%] seaicecp.dataset.trim_dataset
[AutoAPI] Rendering Data... [ 89%] seaicecp.params.latlon_params
[AutoAPI] Rendering Data... [ 93%] seaicecp.dataset.set_date_type
[AutoAPI] Rendering Data... [ 96%] seaicecp.path.manipulate_paths
[AutoAPI] Rendering Data... [100%] seaicecp.dataset.example_dataset

[autosummary] generating autosummary for: autoapi/index.rst, autoapi/seaicecp/dataset/date_type/index.rst, autoapi/seaicecp/dataset/example_dataset/index.rst, autoapi/seaicecp/dataset/field_mean/index.rst, autoapi/seaicecp/dataset/get_variable/index.rst, autoapi/seaicecp/dataset/grid_type/index.rst, autoapi/seaicecp/dataset/index.rst, autoapi/seaicecp/dataset/set_date_type/index.rst, autoapi/seaicecp/dataset/tmp/index.rst, autoapi/seaicecp/dataset/trim_dataset/index.rst, ..., docs_setup/HighResMIP_choices.md, docs_setup/data_dir_structure.md, docs_setup/esgpull_downloads.md, docs_setup/globus_downloads.md, docs_setup/initial_setup.md, docs_setup/installation.md, docs_setup/jupyter_test.md, docs_setup/start_container.md, example.ipynb, index.md
building [mo]: targets for 0 po files that are out of date
writing output... 
building [html]: targets for 28 source files that are out of date
updating environment: 0 added, 28 changed, 0 removed
reading sources... [100%] autoapi/seaicecp/verify/verify_path/index
/workspace/docs/autoapi/seaicecp/dataset/field_mean/index.rst:29: WARNING: duplicate object description of seaicecp.dataset.field_mean.cdo, other instance in autoapi/seaicecp/dataset/field_mean/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/dataset/index.rst:144: WARNING: duplicate object description of seaicecp.dataset.cdo, other instance in autoapi/seaicecp/dataset/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/dataset/index.rst:146: WARNING: duplicate object description of seaicecp.dataset.meta_vars, other instance in autoapi/seaicecp/dataset/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/dataset/index.rst:161: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/dataset/trim_dataset/index.rst:30: WARNING: duplicate object description of seaicecp.dataset.trim_dataset.cdo, other instance in autoapi/seaicecp/dataset/trim_dataset/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/dataset/trim_dataset/index.rst:43: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/path/index.rst:269: WARNING: duplicate object description of seaicecp.path.get_model_path, other instance in autoapi/seaicecp/path/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/path/index.rst:301: WARNING: duplicate object description of seaicecp.path.list_available_models, other instance in autoapi/seaicecp/path/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/path/index.rst:388: WARNING: duplicate object description of seaicecp.path.get_variable_path, other instance in autoapi/seaicecp/path/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/plot/hvplots/index.rst:38: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/index.rst:67: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/index.rst:101: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/index.rst:116: WARNING: duplicate object description of seaicecp.plot.get_limited_extent, other instance in autoapi/seaicecp/plot/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/plot/index.rst:127: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/index.rst:141: WARNING: duplicate object description of seaicecp.plot.save_hvplot, other instance in autoapi/seaicecp/plot/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/plot/index.rst:194: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/index.rst:200: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/limit_extent/index.rst:29: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/seasonal_cycle/index.rst:37: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/seasonal_cycle/index.rst:43: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/time_series/index.rst:34: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/plot/time_series/index.rst:40: WARNING: Definition list ends without a blank line; unexpected unindent. [docutils]
/workspace/docs/autoapi/seaicecp/verify/index.rst:27: WARNING: duplicate object description of seaicecp.verify.verify_path, other instance in autoapi/seaicecp/verify/verify_path/index, use :no-index: for one of them
/workspace/docs/autoapi/seaicecp/verify/verify_path/index.rst:4: WARNING: duplicate object description of seaicecp.verify.verify_path, other instance in autoapi/seaicecp/verify/index, use :no-index: for one of them
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
copying assets... 
copying static files... 
Writing evaluated template result to /workspace/docs/_build/html/_static/basic.css
Writing evaluated template result to /workspace/docs/_build/html/_static/language_data.js
Writing evaluated template result to /workspace/docs/_build/html/_static/documentation_options.js
Writing evaluated template result to /workspace/docs/_build/html/_static/js/versions.js
copying static files: done
copying extra files... 
copying extra files: done
copying assets: done
writing output... [100%] index
generating indices... genindex py-modindex done
highlighting module code... [100%] seaicecp.verify.verify_path
writing additional pages... search done
dumping search index in English (code: en)... done
dumping object inventory... done
...
```

</details>

```console
...
build succeeded, 24 warnings.

The HTML pages are in _build/html.
```

Then, I went into the `docs/html/index.html` in VSCodium, hit the preview button, then the top right menu to open the page in a browser.
The test webpage seems like it rendered properly. 

When troubleshooting, it can be helpful to try making the `html` directory clean and recreating those documents, in case some cached data is causing issues.
```console
(seaicecp) root@<container_id>:/workspace/docs# make clean
Removing everything under '_build'...
```
Then, run the `make html` command again.


### Hosting documentation
[back to top](#initial-setup)

Following [Py-Pkgs section 3.8.5. Hosting documentation online](https://py-pkgs.org/03-how-to-package-a-python#hosting-documentation-online) to be able to have the documentation you are reading hosted on [Read the Docs](https://about.readthedocs.com).
First, a few changes need to be made to the `.readthedocs.yml` file to ensure the documentation can successfully be hosted. 
Upon generating the `cookiecutter` files, the configuration looked like this:
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
    python: "3.13.5"
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
The first is to specify the version of Python as `3.13` instead of `3.13.5` as Read the Docs only recognizes up to the minor version number, not the patch number.
Second, the `jobs` section needs to be changed to use `uv` instead of `poetry`.
I followed an example shown in the GitHub issue for Read the Docs [#11289, Support uv](https://github.com/readthedocs/readthedocs.org/issues/11289). 
The `.readthedocs.yml` file now reads as follows.
```{literalinclude} ../../.readthedocs.yml
:language: yaml
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

Then, I clicked "Next" and confirmed that the file `.readthedocs.yaml` exists already.
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

Now, the documentation for this project is live and available to view at [https://seaicecp.readthedocs.io/en/latest/](https://seaicecp.readthedocs.io/en/latest/).
I put that URL in the "About" section of the GitHub repository under "Website" to make it more visible to people who find the project.


### Enabling $\LaTeX$ math syntax
[back to top](#initial-setup)

In order to be able to use dollar signs to quickly indicate a mathematical symbol from $\LaTeX$, I added the `dollarmath` and `amsmath` extensions to the `docs/conf.py` file's `myst_enable_extensions` list.
```python
myst_enable_extensions = [
    "dollarmath", 
    "amsmath"
]
```
This allows me to render mathematical syntax, such as a speed of `$\sim$ 1 km day$^{−1}$` which renders as $\sim$ 1 km day$^{−1}$. 
See the MyST-Parser documentation page on [Syntax Extensions](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html)


### Enabling easy DOI links
[back to top](#initial-setup)

When making citations in the documentation, it can be cumbersome to link to a DOI.
For example, to cite the EC-Earth3P-HR model, I would type out the link `[doi:10.22033/ESGF/CMIP6.2323](https://doi.org/10.22033/ESGF/CMIP6.2323)` which renders as [doi:10.22033/ESGF/CMIP6.2323](https://doi.org/10.22033/ESGF/CMIP6.2323).
In the documentation of my {doc}`HighResMIP Choices <../docs_data/HighResMIP_choices>`, I make around 50 citations.

To set up a URL scheme that makes DOI links shorter, I added the following to `docs/conf.py`:
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
Now, I can simply type out `<doi:10.22033/ESGF/CMIP6.2323>` which renders as <doi:10.22033/ESGF/CMIP6.2323>, the same link but with many fewer characters.
See the MyST-Parser documentation page on [Customizing external URL resolution](https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html#customising-external-url-resolution) for more information.
