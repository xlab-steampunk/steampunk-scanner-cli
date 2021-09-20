import json
from pathlib import Path
from typing import Optional

import requests
import typer
import yaml

API_ENDPOINT = "http://10.44.17.54/api/scantmp"

app = typer.Typer(help="Quality scanner for Ansible Playbooks")


class SafeLineLoader(yaml.loader.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        mapping['__line__'] = node.start_mark.line + 1
        return mapping


@app.command(help="Initiate Ansible scan")
def scan(file: Path = typer.Argument(..., help="Ansible tasks, playbook or role", exists=True, file_okay=True,
                                     dir_okay=False, writable=False, readable=True, resolve_path=True),
         output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file")):
    with open(str(file), "r") as stream:
        try:
            playbooks = []
            task_lines = []
            playbook_dict = yaml.load(stream, Loader=SafeLineLoader)[0]

            playbook_dict.pop("name", None)
            playbook_dict.pop("hosts", None)
            playbook_dict.pop("__line__", None)

            playbook_tasks = playbook_dict.get("tasks", None)
            for task in playbook_tasks:
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

            playbooks.append(playbook_dict)
            playbook_json = json.dumps({"playbooks": [playbooks]}, indent=2)

            r = requests.post(API_ENDPOINT, data=playbook_json)
            json_response = json.loads(r.text)

            response_tasks = json_response["playbooks"][0]["tasks"]
            iterator = iter(task_lines)
            for task in response_tasks:
                task["line"] = next(iterator, None)

            if output_file:
                with open(output_file, "w+") as outfile:
                    json.dump(json_response, outfile, indent=2)
            else:
                print(json.dumps(json_response, indent=2))
        except Exception as e:
            print(e)


@app.callback()
def callback():
    pass
