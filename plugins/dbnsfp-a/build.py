#!/bin/env python3
import csv
from pathlib import Path
from string import Template

dbnsfp_root_path = Path(f"{__file__}/..").resolve()
base_path = Path(f"{__file__}/../base/").resolve()
entry_point_template = Template("".join(open(base_path / "base-entrypoint.py").readlines()))
base_manifest_template = Template("".join(open(base_path / "base-manifest.yaml").readlines()))

with open("plugins.csv") as plugin_csv_file:
    reader = csv.DictReader(plugin_csv_file)
    for row in reader:
        row["Operator"] = "min" if row["Cutoff"][0] == "<" else "max"
        row["Cutoff"] = "\"" + row["Cutoff"] + "\""
        dir_name = row["Name"].strip().lower()
        plugin_path = dbnsfp_root_path / dir_name
        plugin_path.mkdir()
        with open(plugin_path / "manifest.yaml","w") as plugin_yaml_file:
            plugin_yaml_file.write(base_manifest_template.substitute(row))
        with open(plugin_path / "entrypoint.py","w") as entry_point_file:
            entry_point_file.write(entry_point_template.substitute(row))
