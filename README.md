# Sentinels by Thinkst Canary

<img src="https://raw.githubusercontent.com/thinkst/sentinels/master/docs/logo.png" width="50" style="float: left"> Sentinels is a multi-protocol network honeypot. It's primary use-case is to catch hackers after they've breached non-public networks. It has extremely low resource requirements and can be tweaked, modified, and extended.

[![Sentinels Tests](https://github.com/thinkst/sentinels/actions/workflows/sentinels_tests.yml/badge.svg)](https://github.com/thinkst/sentinels/actions/workflows/sentinels_tests.yml)
[![Docker build](https://github.com/thinkst/sentinels/actions/workflows/docker-build.yml/badge.svg)](https://github.com/thinkst/sentinels/actions/workflows/docker-build.yml)
[![Publish to PyPI](https://github.com/thinkst/sentinels/actions/workflows/publish.yml/badge.svg)](https://github.com/thinkst/sentinels/actions/workflows/publish.yml)

## Overview

Sentinels runs as a daemon and implements multiple common network protocols. When attackers breach networks and interact with the honeypot, Sentinels will send you alerts via a variety of mechanisms.

Sentinels is implemented in Python, so the core honeypot is cross-platform; however, certain features require specific OSes. Running on Linux will give you the most options. It has extremely low resource requirements; for example, it can be deployed happily on a Raspberry Pi or a VM with minimal resources.

This README describes how to install and configure Sentinels on Ubuntu Linux and MacOS.

Sentinels is the Open Source version of our commercial [Thinkst Canary](https://canary.tools) honeypot.

## Enterprise Extensions (Advanced Sentinels)
This repository includes advanced enterprise-grade additions that push Sentinels to the bleeding edge of deception technology:
* **Automated Noise Filtering:** A built-in time-series correlation engine in `logger.py` that suppresses alert fatigue by filtering out known internet scanners.
* **Threat Intelligence Auto-Scoring:** Real-time IP extraction and Threat Intel scoring automatically appended to the JSON logs.
* **Terraform Infrastructure as Code (IaC):** An automated EKS Kubernetes cluster and VPC deployment setup located in `terraform/`.
* **Advanced HTTP Skins:** New highly-targeted honeypot web skins for WordPress, Jenkins, and Confluence logins.
* **Decentralized Sensors:** A silent `iptables` proxy script (`sensors/proxy_sensor.sh`) that turns any production Linux server into a forwarder for the central Sentinels cluster.
* **High-Interaction Proxying Trigger:** A simulated high-interaction handoff in the SSH module to track advanced persistence.
* **CanaryTokens Engine:** A utility (`bin/embed_canarytokens.py`) to automatically drop fake AWS credentials and tracking documents into SMB/FTP shares.

## Table of Contents
- **[Prerequisites](#prerequisites)**
- **[Features](#features)**
- **[Installation](#installation)**
  - [Installation on Ubuntu](#installation-on-ubuntu)
  - [Installation on macOS](#installation-on-macos)
  - [Installation via Git](#installation-via-git)
  - [Installation for Docker](#installation-for-docker)
- **[Configuring Sentinels](#configuring-sentinels)**
  - [Creating the initial configuration](#creating-the-initial-configuration)
  - [Enabling protocol modules and alerting](#enabling-protocol-modules-and-alerting)
  - [Optional modules](#optional-modules)
     - [SNMP](#snmp)
     - [Portscan](#portscan)
     - [Samba Setup](#samba-setup)
- **[Running Sentinels](#running-sentinels)**
  - [Directly on Linux or macOS](#directly-on-linux-or-macos)
  - [With docker compose](#with-docker-compose)
  - [With Docker](#with-docker)
- **[Documentation](#documentation)**
- **[Project Participation](#project-participation)**
  - [Contributing](#contributing)
  - [Security Vulnerability Reports](#security-vulnerability-reports)
  - [Bug reports](#bug-reports)
  - [Feature Requests](#feature-requests)
  - [Code of Conduct](#code-of-conduct)

## Prerequisites

* AMD64: Python 3.10+
* ARM64: Python 3.10+
* _Optional_ SNMP requires the Python library Scapy
* _Optional_ Samba module needs a working installation of Samba
* _Optional_ Portscan uses iptables (not nftables) and is only supported on Linux-based operating systems

## Features

* Mimic an array of network-accessible services for attackers to interact with.
* Receive various alerts as soon as potential threats are detected, highlighting the threat source IP address and where the breach may have occurred.

## Installation

The Sentinels installation essentially involves ensuring the Python environment is ready, then installing the Sentinels Python package (plus optional extras).

If `uv` is installed, you can use it for virtual environment creation and package installation. If it is not installed, the standard `python`/`pip` flow below continues to work.

### Installation on Ubuntu

Installation on Ubuntu 22.04 LTS or 24.04 LTS:
```
$ sudo apt-get install python3-dev python3-pip python3-virtualenv python3-venv python3-scapy libssl-dev libpcap-dev
$ virtualenv env/
$ . env/bin/activate
$ pip install sentinels
```

Optional `uv` equivalent:
```
$ uv venv env
$ . env/bin/activate
$ uv pip install sentinels
```

Optional extras (if you wish to use the Windows File Share module, and the SNMP module):
```
$ sudo apt install samba # if you plan to use the Windows File Share module
$ pip install scapy pcapy-ng # if you plan to use the SNMP module
```

### Installation on macOS

First, create and activate a new Python virtual environment:
```
$ virtualenv env/
$ . env/bin/activate
```

Optional `uv` equivalent:
```
$ uv venv env
$ . env/bin/activate
```

Macports users should then run:
```
$ sudo port install openssl
$ env ARCHFLAGS="-arch x86_64" LDFLAGS="-L/opt/local/lib" CFLAGS="-I/opt/local/include" pip install cryptography
```

Alternatively, Homebrew x86 users run:
````
$ brew install openssl
$ env ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install cryptography
````

Homebrew M1 users run:
```
$ brew install openssl
$ env ARCHFLAGS="-arch arm64" LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib" CFLAGS="-I/opt/homebrew/opt/openssl@1.1/include" pip install cryptography
```

(The compilation step above is necessary as multiple OpenSSL versions may exist, which can confound the Python libraries.)

Now the installation can run as usual:
```
$ pip install sentinels
$ pip install scapy pcapy-ng # optional
```

With `uv` installed, the equivalent commands are:
```
$ uv pip install sentinels
$ uv pip install scapy pcapy-ng # optional
```

The Windows File Share (smb) module is not available on macOS.

### Installation via Git

To install from source, instead of running pip do the following:

```
$ git clone https://github.com/thinkst/sentinels
$ cd sentinels
$ python setup.py sdist
$ cd dist
$ pip install sentinels-<version>.tar.gz
```

With `uv` installed, you can replace the final install step with:
```
$ uv pip install sentinels-<version>.tar.gz
```

### Use via pkgx

Sentinels is packaged via [pkgx](https://pkgx.sh/), so no installation is needed if pkgx is installed, simply preface the `sentinelsd` command with
`pkgx`. Due to environment variable protections in modern `sudo` implementations, the entire command must be run as root, or via `sudo -E`.

```
$ pkgx sentinelsd --version
```

### Installation for Docker

Sentinels Docker images are hosted on Docker Hub. These are only useful on Linux Docker hosts, as the `host` network engine is required for accurate network information.

## Configuring Sentinels

### Creating the initial configuration

When Sentinels starts it looks for config files in the following locations and will stop when the first configuration is found:

1. `./sentinels.conf` (i.e. the directory where Sentinels is installed)
2. `~/.sentinels.conf` (i.e. the home directory of the user, usually this will be `root` so `/root/.sentinels.conf`)
3. `/etc/sentinelsd/sentinels.conf`

To create an initial configuration, run as `root` (you may be prompted for a `sudo` password):
```
$ sentinelsd --copyconfig
[*] A sample config file is ready /etc/sentinelsd/sentinels.conf

[*] Edit your configuration, then launch with "sentinelsd --start --uid=nobody --gid=nogroup"
```

This creates the path and file `/etc/sentinelsd/sentinels.conf`. You must now edit the config file to determine which services and logging options you want to enable.

### Enabling protocol modules and alerting

Configuration is performed via the JSON config file. Edit the file, and when happy save and exit.

### Optional modules

#### SNMP

The `snmp` module is only available when Scapy is present. See the installation steps for SNMP above.

#### Portscan

The `portscan` module is only available on Linux hosts, as it modifies `iptables` rules.

Please note that for the Portscan service, we have added a `portscan.ignore_localhost` setting, which means the Sentinels `portscan` service will ignore (not alert on) port scans originating for the localhost IP (`127.0.0.1`). This setting is false by default.

#### Samba Setup

The Windows File Share module (`smb`) requires a Samba installation. See a step-by-step guide on [the Wiki](https://github.com/thinkst/sentinels/wiki/Opencanary-and-Samba).

## Running Sentinels

Sentinels is either run directly on a Linux or macOS host, or via a Docker container.

### Directly on Linux or macOS

Start Sentinels by running:

```
$ . env/bin/activate
$ sentinelsd --start --uid=nobody --gid=nogroup
```

With the `uid` and `gid` flags, Sentinels drops root privileges after binding to its ports. This can be changed to other low-privileged user/group or omitted to keep running with root privileges.

### With pkgx

Start Sentinels by running:

```
$ sudo -E pkgx sentinelsd --start --uid=nobody --gid=nogroup
```

With the `uid` and `gid` flags, Sentinels drops root privileges after binding to its ports. This can be changed to other low-privileged user/group or omitted to keep running with root privileges.


### With docker compose

The route requires [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) to be installed.

> **Note**
> The portscan module is automatically disabled for Dockerised Sentinels.

1. Edit the `data/.sentinels.conf` file to enable, disable or customize the services that will run.
1. Edit the `ports` section of the `docker-compose.yml` file to enable/disable the desired ports based on the services you have enabled in the config file.
1. Run the container.
    ```bash
    docker compose up latest
    ```

To view the logs run `docker compose logs latest`.

To stop the container run `docker compose down`.

To build your own Docker Sentinels using `docker compose`, head over to our [wiki](https://github.com/thinkst/sentinels/wiki/Using-Dockerised-Sentinels#building-and-running-your-own-docker-sentinels-image-with-docker-compose)

### With Docker

Please head over our dedicated Docker [wiki](https://github.com/thinkst/sentinels/wiki/Using-Dockerised-Sentinels#building-and-running-your-own-docker-sentinels-image-with-docker) for everything Dockerised Sentinels.

### With Ansible

Please head over to our forked repository for an Ansible Sentinels role over [here](https://github.com/thinkst/ansible-role-sentinels).
## Documentation

* The [Wiki](https://github.com/thinkst/sentinels/wiki) contains our FAQ.
* Additional documentation is available on our [main site](https://sentinels.org).

## Project Participation

### Contributing

We welcome PRs to this project. Please read our [Code of Conduct](https://github.com/thinkst/.github/blob/master/CODE_OF_CONDUCT.md) and [Contributing](https://github.com/thinkst/.github/blob/master/CONTRIBUTING.md) documents before submitting a pull request.

At a minimum you should run `pre-commit` before submitting the PR. Install and run it in the same Python environment that Sentinels is installed into:
```
$ pip install pre-commit
# Do work
$ git add file
$ pre-commit
$ git add file # only run this if pre-commit auto-fixed the file
$ git commit
```

### Security Vulnerability Reports

See our [Security Policy](https://github.com/thinkst/sentinels/security/policy) for details on how to report security vulnerabilities.

### Bug reports

Please file bug reports on [Github](https://github.com/thinkst/sentinels/issues) using the template we provide.

### Feature Requests

Feature requests are tracked [here](https://github.com/thinkst/sentinels/discussions/categories/feature-requests).

### Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](https://github.com/thinkst/.github/blob/master/CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to github@thinkst.com.
