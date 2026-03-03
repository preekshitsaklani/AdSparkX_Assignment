#!/usr/bin/env python3
"""Build the PACSA notebook from separate cell files."""
import json, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

cells = []
for fname in sorted(os.listdir("cells")):
    fpath = os.path.join("cells", fname)
    with open(fpath) as fh:
        src = fh.read()
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]]
    if lines[-1]:
        source.append(lines[-1])

    if fname.endswith(".md"):
        cells.append({"cell_type": "markdown", "metadata": {}, "source": source})
    else:
        cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source})

nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.10.0"}},
    "cells": cells,
}

with open("PACSA_Agent.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
print("Done:", len(cells), "cells")
