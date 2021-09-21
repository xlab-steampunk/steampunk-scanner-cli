from pathlib import Path
from typing import Optional

import typer
import yaml
from utils import parse_tasks_or_playbook, parse_role, scan_ansible

API_ENDPOINT = "http://10.44.17.54/api/scantmp"

app = typer.Typer(help="Quality scanner for Ansible Playbooks")


class SafeLineLoader(yaml.loader.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        mapping['__line__'] = node.start_mark.line + 1
        return mapping


@app.command(help="Initiate Ansible scan")
def scan(path: Path = typer.Argument(..., help="Ansible tasks, playbook or role", exists=True, file_okay=True,
                                     dir_okay=True, writable=False, readable=True, resolve_path=True),
         output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file")):
    if path.is_file():
        playbooks, task_lines = parse_tasks_or_playbook(path)
        scan_ansible(API_ENDPOINT, playbooks, task_lines, output_file)
    elif path.is_dir():
        joined_tasks, joined_task_lines = parse_role(path)
        scan_ansible(API_ENDPOINT, joined_tasks, joined_task_lines, output_file)
    else:
        raise Exception("Unrecognized input file.")


@app.callback()
def callback():
    pass
