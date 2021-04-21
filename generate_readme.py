#!/usr/bin/env python3


import pathlib
import json
from pprint import pprint as pp


title = "Eris' Cogs"
desc = "Welcome to my cogs!"

readme = (
    f"# {title}\n{desc}\n\nThe table below lists all available cogs, "
    "as well as their current state. If a cog is listed as 'not ready' "
    "that simply means that I haven't gone through to productionalize / standardize "
    "the code. They still work, I just haven't cleaned them up entirely yet. "
    "Use at your own risk!\n\nIf you're on windows, "
    f"you'll need to delete the symlinked `eris_event_lib.py` "
    f"files in the directories of the cogs you wish to install "
    f"and replace it with a copy of the root-level file.\n\n"
)

meta_keys = [
    "short",
    "description",
    # "author",
]

all_dirs = [
    d for d in pathlib.Path().glob("*") if not d.name.startswith(".") and d.is_dir()
]
all_dirs = sorted(all_dirs)

all_entries = []
table = []
for d in all_dirs:
    name = d.name.capitalize()
    meta = json.loads((d / "info.json").read_text())

    new_entry = f"## {name}\n"

    demofile = d / "demo.png"
    if demofile.exists():
        new_entry += f"![png]({demofile})\n\n"

    meta_entries = []
    for k in meta_keys:
        val = meta.get(k)
        if k == "author":
            val = ", ".join(val)
        if val:
            val = val.replace("\n", "\n\n")
        meta_entries.append(f"{k.capitalize()}: {val}")
    new_entry += "\n\n".join(meta_entries)
    all_entries.append(new_entry)

    table.append((name, f"[{name}](#{name.lower()})", f"{meta.get('short')}", f"{'✅' if meta.get('ready', False) else '❌'}"))

table = sorted(table, key=lambda tup: (tup[3] != "✅", tup[0]))
table = ['| ' + ' | '.join(row[1:]) + ' |' for row in table]
table = ["| Cog Name | Short | Ready? |", "| --- | --- | --- |"] + table

readme += "\n".join(table)
readme += "\n\n"
readme += "\n".join(all_entries)

readmefile = pathlib.Path() / "README.md"
readmefile.write_text(readme)
