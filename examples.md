# Examples of requests and responses

This document contains examples of things that the API expects to receive and
the things API returns.


## Playbook input

Let us assume we have the following playbook:

    ---
    - name: Sample playbook
      hosts: localhost

      collections:
        - sensu.sensu_go
        - ansible.builtin

      tasks:
        - name: Create local user
          usr:
            name: johnmcclane

        - name: OpenStack info gathering
          openstack.cloud.os_flavor_info:

        - name: Create Sensu Go user
          user:
            username: joe
            password: "{{ lookup('env', 'SENSU_USER_PASSWORD') }}"

        - name: Manage PHP dependencies
          composer:
            working-dir: /tmp

        - name: Run command
          ansible.builtin.shell: touch /tmp/lock

        - name: Read-only command
          ansible.builtin.command: ls /tmp
          changed_when: false

We expect the CLI tool to convert this tho the following payload:

    [
      {
        "usr": ["name"],
        "collections": [
          "sensu.sensu_go",
          "ansible.builtin"
        ],
        # Anything else is ignored, but can be sent back without any issues.
        "__file__": "/full/ath/to/source/file.yaml",
        "__line__": 10
      },
      {
        "openstack.cloud.os_flavor_info": null,
        "collections": [
          "sensu.sensu_go",
          "ansible.builtin"
        ],
        "__file__": "/full/ath/to/source/file.yaml",
        "__line__": 14
      },
      {
        "user": ["username", "password"],
        "collections": [
          "sensu.sensu_go",
          "ansible.builtin"
        ],
        "__file__": "/full/ath/to/source/file.yaml",
        "__line__": 17
      },
      {
        "composer": ["working-dir"],
        "collections": [
          "sensu.sensu_go",
          "ansible.builtin"
        ],
        "__file__": "/full/ath/to/source/file.yaml",
        "__line__": 22
      },
      {
        "ansible.builtin.shell": null,
        "collections": [
          "sensu.sensu_go",
          "ansible.builtin"
        ],
        "__file__": "/full/ath/to/source/file.yaml",
        "__line__": 26
      },
      {
        "ansible.builtin.command": null,
        "changed_when": null,
        "collections": [
          "sensu.sensu_go",
          "ansible.builtin"
        ],
        "__file__": "/full/ath/to/source/file.yaml",
        "__line__": 29
      }
    ]

The server will respond with somethign similar to this:

    [
      {
        "certified": false,
        "errors": [
          "Cannot find module information in the database. Is this a custom module not published on Ansible Galaxy?"
        ],
        "fqcn": null,
        "hints": []
      },
      {
        "certified": false,
        "errors": [],
        "fqcn": "openstack.cloud.compute_flavor_info",
        "hints": [
          "Module is deprecated. os_ prefixed module names are deprecated, use openstack.cloud.compute_flavor_info",
          "The 'openstack.cloud.os_flavor_info' module is redirected to the 'openstack.cloud.compute_flavor_info' module. You should use fully-qualified collection name to avoid future problems."
        ]
      },
      {
        "certified": true,
        "errors": [
          "'username' is not a valid parameter.",
          "'name' is a required parameter."
        ],
        "fqcn": "sensu.sensu_go.user",
        "hints": [
          "Potential name clashes for user between ansible.builtin.user, sensu.sensu_go.user",
          "The 'user' module is redirected to the 'sensu.sensu_go.user' module. You should use fully-qualified collection name to avoid future problems."
        ]
      },
      {
        "certified": false,
        "errors": [],
        "fqcn": "community.general.composer",
        "hints": [
          "The 'composer' module is redirected to the 'community.general.composer' module. You should use fully-qualified collection name to avoid future problems.",
          "'working-dir' is deprecated in favor of working_dir."
        ]
      },
      {
        "certified": true,
        "errors": [],
        "fqcn": "ansible.builtin.shell",
        "hints": [
          "The task does not enforce a state. Use 'creates' or 'removes' parameters to inform Ansible under what conditions it should run the command. If the executed command is enforcing the desired state by itself already, use the 'changed_when' keyword to inform Ansible when the state changed. The last two options are adding a 'when' clause to the task or converting current task into a handler."
        ]
      },
      {
        "certified": true,
        "errors": [],
        "fqcn": "ansible.builtin.command",
        "hints": []
      }
    ]


Sample `curl` command:

    curl \
      --request POST \
      --header "Content-Type: application/json" \
      --data @request_data.json \
      http://10.44.17.54/api/scantmp
    | jq .
