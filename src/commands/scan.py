import argparse
import json
import os
from getpass import getpass
from pathlib import Path

import requests

from src.cli import API_ENDPOINT
from src.helpers import prepare_scan_output, AnsibleEntity, parse_ansible_entities


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
        "--output", "-o", type=str, help="Output file location"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace):
    """
    Invoke the Ansible scanner and print/save the scan result
    :param args: Argparse arguments
    """
    try:
        scanner_username = os.getenv("SCANNER_USERNAME")
        scanner_password = os.getenv("SCANNER_PASSWORD")
        if not scanner_username:
            scanner_username = input("Username: ")
        if not scanner_password:
            scanner_password = getpass()

        input_tasks = []
        if args.tasks:
            input_tasks += parse_ansible_entities(args.tasks, AnsibleEntity.TASK)
        if args.playbooks:
            input_tasks += parse_ansible_entities(args.playbooks, AnsibleEntity.PLAYBOOK)
        if args.roles:
            input_tasks += parse_ansible_entities(args.roles, AnsibleEntity.ROLE)
        if args.collections:
            input_tasks += parse_ansible_entities(args.collections, AnsibleEntity.COLLECTION)

        response = requests.post(f"{API_ENDPOINT}/scantmp", data=json.dumps(input_tasks, indent=2),
                                 auth=(scanner_username, scanner_password))
        if response.ok:
            output_tasks = json.loads(response.text)
            scan_output = prepare_scan_output(input_tasks, output_tasks)

            if args.output:
                with open(args.output, "w+") as outfile:
                    outfile.write(scan_output)
            else:
                print(scan_output)
        else:
            print(f"API error: {response.status_code} - {response.reason}")
            exit(1)
    except Exception as e:
        print(e)
        exit(1)
