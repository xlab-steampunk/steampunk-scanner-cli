# Examples of cli usage

This document describes what CLI options program should accept and how the
errors and notes should be reported back.


## Switches

The cli command should accept 4 different switches. The first one is the
`--playbooks` switch:

    $ scanner --playbooks path/to/playbook1.yaml [path/to/playbook2.yaml ...]

This should load the playbooks and parse them. The switch should accept
multiple filenames so that we can do something like this:

    $ scanner --playbooks path/to/playbook/folder/play_*.yaml

The second switch cli command should accept is the `--tasks` switch:

    $ scanner --tasks path/to/playbook1.yaml [path/to/playbook2.yaml ...]

This behave exactly the same as the playbook switch, but it parses a tasks
file, which is just unindented `tasks` section of the playbook.

The third switch is `--roles`:

    $ scanner --roles path/to/role1 [path/to/role2 ...]

Since roles are a bit more complex, the functionality here is also a bit more
complex. Scanner should recursivelly load files from the `path/to/role1/tasks`
and `path/to/role1/handlers` folders. Those files are tasks files, so parsing
should be trivial. One can imagine that roles switch is convrted to something
like this:

    $ scanner --tasks \
        $(find path/to/role1/tasks -type f | egrep "ya?ml$") \
        $(find path/to/role1/handlers -type f | egrep "ya?ml$")

Last switch I would like to add, but is optional at this point (we will add it
only if the time permits) is the `--collection`:

    $ scanner --collection path/to/collection1 [path/to/collection2 ...]

This should behave the same way as calling:

    $ scanner \
        --roles path/to/collection1/roles/* \
        --playbooks path/to/collection1/playbooks/*


## Output

Let us assume we have the following `playbook.yaml` file:

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
    16 
    17     - name: Create Sensu Go user
    18       user:
    19         username: joe
    20         password: "{{ lookup('env', 'SENSU_USER_PASSWORD') }}"
    21 
    22     - name: Manage PHP dependencies
    23       composer:
    24         working-dir: /tmp
    25 
    26     - name: Run command
    27       ansible.builtin.shell: touch /tmp/lock
    28 
    29     - name: Read-only command
    30       ansible.builtin.command: ls /tmp
    31       changed_when: false

In this case, we expect cli tool to report something like that back:

    $ scanner --playbook.yaml
    playbook.yaml:10: ERROR: Cannot find module information in the database. Is this a custom module not published on Ansible Galaxy?
    playbook.yaml:14: HINT: Module is deprecated. os_ prefixed module names are deprecated, use openstack.cloud.compute_flavor_info.
    playbook.yaml:14: HINT: The 'openstack.cloud.os_flavor_info' module is redirected to the 'openstack.cloud.compute_flavor_info' module. You should use fully-qualified collection name to avoid future problems.
    playbook.yaml:14: WARNING: The 'openstack.cloud.os_flavor_info' module is not certified.
    ...
