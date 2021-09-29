# Steampunk Scanner CLI

This project brings a Command Line Interface (CLI) for the [Steampunk Scanner]
(developed by [XLAB Steampunk]).


## Table of Contents

  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
      - [Registration](#registration)
      - [Scanning](#scanning)
          - [Tasks](#tasks)
          - [Playbooks](#playbooks)
          - [Roles](#roles)
          - [Collections](#collections)
  - [Acknowledgement](#acknowledgement)


## Introduction

The [Steampunk Scanner] is a quality scanner for Ansible playbooks, where you
can scan the playbook and get an instant quality score with tips on how to
improve it. The [steampunk-scanner] CLI enables the use of Ansible scanner from
the console with the ability to scan Ansible task files, playbooks, roles and
collections.


## Prerequisites

The `steampunk-scanner` requires Python 3 (and a virtual environment if you do
not want to install it as a user or globally). In a typical modern Linux
environment, we should already be set.  In Ubuntu, however, we might need to
run the following commands:

```console
$ sudo apt update
$ sudo apt install -y python3-venv python3-wheel python-wheel-common
```


## Installation

The `steampunk-scanner` CLI tool is available as a Python package, so the
simplest way to test it, is to install it into a fresh Python virtual
environment like this:

```console
$ python3 -m venv .venv && . .venv/bin/activate
(.venv) $ pip install steampunk-scanner
```

The tool is available on PyPI as a package named [steampunk-scanner]. Apart
from the latest [PyPI production] version, you can also find the latest [PyPI
development] version, which includes pre-releases so that you will be able to
test the latest features before they are officially released.


## Usage

After the CLI is installed, you can explore its commands and options by running
`steampunk-scanner --help`.


### Registration

To use the CLI you have to register a new or use your existing Steampunk
Scanner user account.

To register a new user with your email, use the `register` command like this:

```bash
(.venv) $ steampunk-scanner account register email@example.com
Password:
```

After that step, your account is still pending for activation.  We will send
you an email with an activation code, which you can use like that:

```bash
(.venv) $ steampunk-scanner account activate email@example.com <activation code>
```

If everything goes okay you have successfully registered your Steampunk Scanner
user account.  To use it for scanning, you should set `SCANNER_USERNAME` and
`SCANNER_PASSWORD` environment variables and then you can start scanning right
away (you will be prompted for your credentials if you skip setting those env
vars).


### Scanning

The CLI `scan` command is used for Ansible scanning and returning back the scan
results. It accepts for different switches for different Ansible entities
(tasks, playbooks, roles and collections).

```bash
# scan Ansible task file, which is just unindented `tasks` section of the playbook
(.venv) $ steampunk-scanner scan \
    --tasks path/to/taskfile1.yaml

# scan Ansible playbooks
(.venv) $ steampunk-scanner scan \
    --playbooks path/to/playbook1.yaml path/to/playbook2.yaml

# scan multiple Ansible playbooks using glob
(.venv) $ steampunk-scanner scan \
    --playbooks path/to/playbook/folder/play_*.yaml

# scan Ansible role (scans tasks and handlers)
(.venv) $ steampunk-scanner scan \
    --roles path/to/role1 path/to/role2

# scan Ansible collection (scans collection roles and playbooks)
(.venv) $ steampunk-scanner scan \
    --collections path/to/collection1 path/to/collection2

# scan multiple Ansible entities at once
(.venv) $ steampunk-scanner scan \
    --tasks path/to/taskfile.yaml \
    --playbooks path/to/playbook.yaml \
    --roles path/to/role \
    --collections path/to/collection
```


#### Tasks

Let us assume we have the following `taskfile.yaml` file:

```
 1 ---
 2 - name: Configure agent (Linux)
 3   include_tasks: linux/configure.yml
 4   when: ansible_facts.os_family != "Linux"
 5
 6 - name: Configure agent (Windows)
 7   include_tasks: windows/configure.yml
 8   when: ansible_facts.os_family == "Windows"
```

In this case, the CLI tool will report something like that back:

```
(.venv) $ steampunk-scanner scan --tasks taskfile.yaml
taskfile.yaml:2: HINT: The 'include_tasks' module is redirected to the
  'ansible.builtin.include_tasks' module. You should use fully-qualified
  collection name to avoid future problems.
taskfile.yaml:6: HINT: The 'include_tasks' module is redirected to the
  'ansible.builtin.include_tasks' module. You should use fully-qualified
  collection name to avoid future problems.
```


#### Playbooks

Let us assume we have the following Ansible playbook `playbook.yaml` file:

```
 1 ---
 2 - name: Sample playbook
 3   hosts: localhost
 4
 5   collections:
 6     - sensu.sensu_go
 7     - ansible.builtin
 8
 9   tasks:
10     - name: Create local user
11       usr:
12         name: johnmcclane
13
14     - name: OpenStack info gathering
15       openstack.cloud.os_flavor_info:
```

In this case, the CLI tool will report something like that back:

```
(.venv) $ steampunk-scanner scan --playbooks playbook.yaml
playbook.yaml:10: ERROR: Cannot find module information in the database. Is
  this a custom module not published on Ansible Galaxy?
playbook.yaml:14: HINT: Module is deprecated. os_ prefixed module names are
  deprecated, use openstack.cloud.compute_flavor_info.
playbook.yaml:14: HINT: The 'openstack.cloud.os_flavor_info' module is
  redirected to the 'openstack.cloud.compute_flavor_info' module. You should
  use fully-qualified collection name to avoid future problems.
playbook.yaml:14: WARNING: The 'openstack.cloud.os_flavor_info' module is not
  certified.
```

#### Roles

Let us assume we have an Ansible role (for example from [Sensu Go Ansible
Collection]) with the following structure:

```console
(.venv) $ tree sensu-go/roles/backend/
sensu-go/roles/backend/
├── defaults
│   └── main.yml
├── handlers
│   └── main.yml
├── meta
│   ├── argument_specs.yml
│   └── main.yml
├── README.md
├── tasks
│   ├── configure.yml
│   ├── main.yml
│   └── start.yml
├── templates
│   └── backend.yml.j2
└── vars
    └── main.yml
```

In this case, the CLI tool will scan `tasks` and `handlers` and report something like that back:

```
(.venv) $ steampunk-scanner scan --roles sensu-go/roles/backend/
sensu-go/roles/backend/tasks/start.yml:2: HINT: The 'service' module is
  redirected to the 'ansible.builtin.service' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/start.yml:8: ERROR: 'cmd' is not a valid parameter.
sensu-go/roles/backend/tasks/start.yml:8: HINT: The 'command' module is
redirected to the 'ansible.builtin.command' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/start.yml:16: ERROR: 'cmd' is not a valid parameter.
sensu-go/roles/backend/tasks/start.yml:16: HINT: The 'command' module is
  redirected to the 'ansible.builtin.command' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/configure.yml:2: HINT: The 'copy' module is
  redirected to the 'ansible.builtin.copy' module. You should use fully-qualified
  collection name to avoid future problems.
sensu-go/roles/backend/tasks/configure.yml:29: HINT: The 'copy' module is
  redirected to the 'ansible.builtin.copy' module. You should use fully-qualified
  collection name to avoid future problems.
sensu-go/roles/backend/tasks/configure.yml:47: HINT: The 'copy' module is
  redirected to the 'ansible.builtin.copy' module. You should use fully-qualified
  collection name to avoid future problems.
sensu-go/roles/backend/tasks/configure.yml:63: HINT: The 'template' module is
  redirected to the 'ansible.builtin.template' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/main.yml:2: HINT: The 'include_role' module is
  redirected to the 'ansible.builtin.include_role' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/main.yml:8: ERROR: 'manage_sensu_backend_service'
  is not a valid parameter.
sensu-go/roles/backend/tasks/main.yml:8: ERROR: 'key_value' is a required parameter.
sensu-go/roles/backend/tasks/main.yml:8: HINT: The 'set_fact' module is
  redirected to the 'ansible.builtin.set_fact' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/main.yml:12: HINT: The 'include_tasks' module is
  redirected to the 'ansible.builtin.include_tasks' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/main.yml:15: HINT: The 'include_tasks' module is
  redirected to the 'ansible.builtin.include_tasks' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/handlers/main.yml:2: HINT: The 'service' module is
  redirected to the 'ansible.builtin.service' module. You should use
  fully-qualified collection name to avoid future problems.
```

#### Collections

Let us assume we have an Ansible collection (for instance [Sensu Go Ansible
Collection]) with the following structure:

```
(.venv) $ ls -l sensu-go/
total 116
drwxrwxr-x 2 user user  4096 Sep  6 09:28 changelogs
-rw-rw-r-- 1 user user  8589 Sep  6 09:28 CODE_OF_CONDUCT.md
-rw-rw-r-- 1 user user     7 Sep  6 09:28 collection.requirements
-rw-rw-r-- 1 user user 35148 Sep  6 09:28 COPYING
drwxrwxr-x 2 user user  4096 Sep  6 09:28 docker
drwxrwxr-x 5 user user  4096 Sep  6 09:28 docs
-rw-rw-r-- 1 user user    46 Sep  6 09:28 docs.requirements
-rw-rw-r-- 1 user user   529 Sep  6 09:28 galaxy.yml
-rw-rw-r-- 1 user user   348 Sep  6 09:28 integration.requirements
-rw-rw-r-- 1 user user  2828 Sep  6 09:28 Makefile
drwxrwxr-x 2 user user  4096 Sep  6 09:28 meta
drwxrwxr-x 7 user user  4096 Sep  6 09:28 plugins
-rw-rw-r-- 1 user user    31 Sep  6 09:28 pytest.ini
-rw-rw-r-- 1 user user  1415 Sep  6 09:28 README.md
drwxrwxr-x 5 user user  4096 Sep 28 10:20 roles
-rw-rw-r-- 1 user user   182 Sep  6 09:28 sanity.requirements
drwxrwxr-x 5 user user  4096 Sep  6 09:28 tests
drwxrwxr-x 2 user user  4096 Sep  6 09:28 tools
drwxrwxr-x 3 user user  4096 Sep  6 09:28 vagrant
```

In this case, the CLI tool will scan `roles` and `playbooks` and report
something like that back:

```
(.venv) $ steampunk-scanner scan --collections sensu-go
sensu-go/roles/backend/tasks/start.yml:2: HINT: The 'service' module is
  redirected to the 'ansible.builtin.service' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/start.yml:8: ERROR: 'cmd' is not a valid parameter.
sensu-go/roles/backend/tasks/start.yml:8: HINT: The 'command' module is
  redirected to the 'ansible.builtin.command' module. You should use
  fully-qualified collection name to avoid future problems.
sensu-go/roles/backend/tasks/start.yml:16: ERROR: 'cmd' is not a valid parameter.
sensu-go/roles/backend/tasks/start.yml:16: HINT: The 'command' module is
  redirected to the 'ansible.builtin.command' module. You should use
  fully-qualified collection name to avoid future problems.
...
```

## Acknowledgement
This tool was created by [XLAB Steampunk], which focuses on smarter Automation with Enterprise Ansible Collections.

[Steampunk Scanner]: https://scanner.steampunk.si/
[XLAB Steampunk]: https://steampunk.si/
[steampunk-scanner]: https://pypi.org/project/steampunk-scanner/
[PyPI production]: https://pypi.org/project/steampunk-scanner/#history
[PyPI development]: https://test.pypi.org/project/steampunk-scanner/#history
[Sensu Go Ansible Collection]: https://galaxy.ansible.com/sensu/sensu_go
