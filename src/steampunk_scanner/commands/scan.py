import argparse
import os
import sys
from getpass import getpass
from pathlib import Path

from steampunk_scanner import api
from steampunk_scanner.helpers import AnsibleEntity, parse_ansible_entities


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "scan", help="Initiate Ansible scan", description="Initiate Ansible scan"
    )
    parser.add_argument(
        "--tasks", "-t", type=lambda p: Path(p).absolute(), nargs='+', help="Paths to file with Ansible tasks"
    )
    parser.add_argument(
        "--playbooks", "-p", type=lambda p: Path(p).absolute(), nargs='+', help="Paths to Ansible playbook file"
    )
    parser.add_argument(
        "--roles", "-r", type=lambda p: Path(p).absolute(), nargs='+', help="Paths to Ansible role directory"
    )
    parser.add_argument(
        "--collections", "-c", type=lambda p: Path(p).absolute(), nargs='+', help="Paths to Ansible collection"
    )
    parser.add_argument(
        "--output", "-o", type=argparse.FileType("w"), help="Output file location", default="-"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace):
    """
    Invoke the Ansible scanner and print/save the scan result
    :param args: Argparse arguments
    """
    username = os.environ.get("SCANNER_USERNAME") or input("Username: ")
    password = os.environ.get("SCANNER_PASSWORD") or getpass()
    client = api.Client(api.ENDPOINT, username, password)

    input_tasks = []
    if args.tasks:
        input_tasks += parse_ansible_entities(args.tasks, AnsibleEntity.TASK)
    if args.playbooks:
        input_tasks += parse_ansible_entities(args.playbooks, AnsibleEntity.PLAYBOOK)
    if args.roles:
        input_tasks += parse_ansible_entities(args.roles, AnsibleEntity.ROLE)
    if args.collections:
        input_tasks += parse_ansible_entities(args.collections, AnsibleEntity.COLLECTION)

    response = client.post("/scan-tasks", input_tasks)
    if response.ok:
        _print_scan_output(args.output, input_tasks, response.json())
    else:
        print(f"API error: {response.status_code} - {response.json()['msg']}")
        sys.exit(1)


def _print_scan_output(out_fh, input_tasks, output_tasks):
    """
    Prints scan output
    :param out_fh: File handle to print result to
    :param input_tasks: Input Ansible task list
    :param output_tasks: Output Ansible task list
    """
    for input_task, output_task in zip(input_tasks, output_tasks):
        file_name = input_task.get("__file__", None)
        task_line = input_task.get("__line__", None)
        certified = output_task.get("certified", False)
        errors = output_task.get("errors", [])
        fqcn = output_task.get("fqcn", None)
        hints = output_task.get("hints", [])

        if fqcn and not certified:
            print(
                f"{file_name}:{task_line}: WARNING: The {fqcn} module is not certified.",
                file=out_fh
            )

        for error in errors:
            print(f"{file_name}:{task_line}: ERROR: {error}", file=out_fh)

        for hint in hints:
            print(f"{file_name}:{task_line}: HINT: {hint}", file=out_fh)

        if errors:
            sys.exit(1)
