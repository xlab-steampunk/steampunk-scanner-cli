# Steampunk Scanner CLI

This project brings a Command Line Interface (CLI) for the [Steampunk Scanner].

## Installation
The `steampunk-scanner` CLI tool is available as a Python package, so the simplest way to test it, is to install it 
into a fresh Python virtual environment like this:

```console
$ git clone ssh://git@gitlab.xlab.si:13022/steampunk/steampunk-scanner/cli.git
$ cd cli
$ python3 -m venv .venv && . .venv/bin/activate
(.venv) $ pip install -e .
```

# Usage
After the CLI is installed, you can start using it like this:

```bash
# print help
(.venv) $ steampunk-scanner --help
# scan Ansible playbooks
(.venv) $ steampunk-scanner --playbooks path/to/playbook1.yaml [path/to/playbook2.yaml ...]
# scan playbooks with regex
(.venv) $ steampunk-scanner --playbooks path/to/playbook/folder/play_*.yaml
# scan Ansible task file, which is just unindented `tasks` section of the playbook
(.venv) $ steampunk-scanner --tasks path/to/playbook1.yaml [path/to/playbook2.yaml ...]
# scan Ansible role (scan task files path/to/role1/tasks and path/to/role1/handlers)
(.venv) $ steampunk-scanner --roles path/to/role1 [path/to/role2 ...]
# scan Ansible collection (scan roles from path/to/collection1/roles/ and playbooks from path/to/collection1/playbooks/)
(.venv) $ steampunk-scanner --collection path/to/collection1 [path/to/collection2 ...]
```

Let us assume we have the following `playbook.yaml` file:

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

```console
$ steampunk-scanner --playbook.yaml
playbook.yaml:10: ERROR: Cannot find module information in the database. Is this a custom module not published on Ansible Galaxy?
playbook.yaml:14: HINT: Module is deprecated. os_ prefixed module names are deprecated, use openstack.cloud.compute_flavor_info.
playbook.yaml:14: HINT: The 'openstack.cloud.os_flavor_info' module is redirected to the 'openstack.cloud.compute_flavor_info' module. You should use fully-qualified collection name to avoid future problems.
playbook.yaml:14: WARNING: The 'openstack.cloud.os_flavor_info' module is not certified.
```

[Steampunk Scanner]: https://scanner.steampunk.si/
