import json
from pathlib import Path
from typing import Optional, List

import requests
import yaml


class SafeLineLoader(yaml.loader.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        mapping['__line__'] = node.start_mark.line + 1
        return mapping


def parse_tasks(tasks: List) -> (List, List):
    task_lines = []

    for task in tasks:
        task.pop("name", None)

        task_line = task.pop("__line__", None)
        if task_line:
            task_lines.append(task_line)

        for task_key in task:
            if type(task[task_key]) is dict:
                task[task_key].pop("__line__", None)
                task[task_key] = list(task[task_key].keys())
            else:
                task[task_key] = None

    return [tasks], task_lines


def parse_playbook(playbook: List) -> (List, List):
    playbook = playbook[0]
    playbook.pop("name", None)
    playbook.pop("hosts", None)
    playbook.pop("__line__", None)

    _, task_lines = parse_tasks(playbook.get("tasks", []))
    return [playbook], task_lines


def parse_tasks_or_playbook(path: Path) -> (List, List):
    with path.open() as stream:
        try:
            yaml_input = yaml.load(stream, Loader=SafeLineLoader)
            if len(yaml_input) == 1:
                return parse_playbook(yaml_input)
            else:
                return parse_tasks(yaml_input)
        except Exception as e:
            print(e)


def parse_role(path: Path) -> (List, List):
    joined_tasks = []
    joined_task_lines = []
    for p in (list((path / "tasks").rglob("*")) + list((path / "handlers").rglob("*"))):
        if p.is_file():
            with p.open() as stream:
                yaml_dict = yaml.load(stream, Loader=SafeLineLoader)
                tasks, task_lines = parse_tasks(yaml_dict)
                joined_tasks += tasks
                joined_task_lines += task_lines
    return joined_tasks, joined_task_lines


def scan_ansible(api_endpoint: str, tasks: List, task_lines: List, output_file: Optional[str]):
    scan_input = json.dumps({"playbooks": [tasks]}, indent=2)

    response = requests.post(api_endpoint, data=scan_input)
    json_response = json.loads(response.text)

    response_tasks = json_response["playbooks"][0]["tasks"]
    iterator = iter(task_lines)
    for task in response_tasks:
        task["line"] = next(iterator, None)

    if output_file:
        with open(output_file, "w+") as outfile:
            json.dump(json_response, outfile, indent=2)
    else:
        print(json.dumps(json_response, indent=2))
