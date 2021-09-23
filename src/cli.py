import argparse
import json
from pathlib import Path

import requests
from helpers import prepare_scan_output, AnsibleEntity, parse_ansible_entities

# change this development API endpoint to a real one when production API auth works and when this CLI is ready
API_ENDPOINT = "http://10.44.17.54/api/scantmp"


def create_parser():
    """
    Create argument parser for CLI
    :return: Parser as argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(description='Quality scanner for Ansible Playbooks')

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

    return parser


def scan(args: argparse.Namespace):
    """
    Invoke Ansible scanner and print the scan result
    :param args: Argparse arguments
    """
    try:
        input_tasks = []
        if args.tasks:
            input_tasks += parse_ansible_entities(args.tasks, AnsibleEntity.TASK)
        if args.playbooks:
            input_tasks += parse_ansible_entities(args.playbooks, AnsibleEntity.PLAYBOOK)
        if args.roles:
            input_tasks += parse_ansible_entities(args.roles, AnsibleEntity.ROLE)
        if args.collections:
            input_tasks += parse_ansible_entities(args.collections, AnsibleEntity.COLLECTION)

        response = requests.post(API_ENDPOINT, data=json.dumps(input_tasks, indent=2))
        if response.ok:
            output_tasks = json.loads(response.text)
            scan_output = prepare_scan_output(input_tasks, output_tasks)

            if args.output:
                with open(args.output, "w+") as outfile:
                    outfile.write(scan_output)
            else:
                print(scan_output)
        else:
            print(f"Error when calling Steampunk Scanner API: {response.status_code} - {response.reason}")
            exit(1)
    except Exception as e:
        print(e)
        exit(1)


def main():
    """
    Main CLI method to be called
    """
    parser = create_parser()
    args = parser.parse_args()
    scan(args)
