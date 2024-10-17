"""
This script calculates coverage statistics for the openMINDS instance library,
i.e. for each instance, which properties have been defined, and for each
terminology, what percentage of instances have a definition for a given property.

Author: Andrew Davison, 2024
"""

import json
from pathlib import Path
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

this_dir = Path(__file__).parent


def read_data(path):
    """Return the data from the JSON file located at `path`"""
    with open(path) as fp:
        data = json.load(fp)
    return data


def get_instance_data():
    """Return the data for all instances in the library."""
    # At present, only covers terminologies
    instance_data = {}
    root = Path("instances/latest")
    for dir in root.iterdir():
        if dir.name == "terminologies":
            instance_data[dir.name] = {}
            for item in dir.iterdir():
                if item.is_dir():
                    instance_data[dir.name][item.name] = {}
                    for subitem in item.iterdir():
                        assert subitem.is_file()
                        instance_data[dir.name][item.name][subitem.name] = read_data(subitem)
                else:
                    instance_data[dir.name][item.name] = read_data(subitem)
    return instance_data


def calculate_stats(instance_data):
    """Calculate coverage statistics across the given instances."""
    stats = {}
    for term_name in sorted(instance_data["terminologies"], key=lambda item: item.lower()):
        instances = instance_data["terminologies"][term_name]
        stats[term_name] = {}
        for key in (
            "definition",
            "description",
            "interlexIdentifier",
            "knowledgeSpaceLink",
            "preferredOntologyIdentifier",
            "synonym",
        ):
            stats[term_name][key] = (
                100
                * sum(
                    int(bool(instance.get(key, None)))
                    for instance in instances.values()
                )
                / len(instances)
            )
    return stats


def colourcode(input):
    """Custom Jinja filter. `input` should be in the range 0-100."""
    if input > 90:
        return "good"
    elif input > 50:
        return "medium"
    else:
        return "bad"


def main(build_dir="_coverage"):
    """Create a set of web pages displaying coverage statistics."""
    env = Environment(loader=FileSystemLoader(this_dir), autoescape=select_autoescape())
    env.filters['colourcode'] = colourcode

    instance_data = get_instance_data()

    stats = calculate_stats(instance_data)

    build_dir = Path(build_dir)
    build_dir.mkdir(exist_ok=True)

    template_home = env.get_template("index.tpl.html")
    context = {
        "terminologies": stats
    }

    with open(build_dir / "index.html", "w") as fp:
        fp.write(template_home.render(**context))
    shutil.copy(this_dir / "coverage.css", build_dir)

    term_dir = build_dir / "terminologies"
    term_dir.mkdir(exist_ok=True)

    template_term = env.get_template("terminology.tpl.html")

    for term_name, value in instance_data["terminologies"].items():
        term_page = term_dir / f"{term_name}.html"
        context = {"term_name": term_name, "instances": value, "stats": stats[term_name]}
        with open(term_page, "w") as fp:
            fp.write(template_term.render(**context))


if __name__ == "__main__":
    main()
