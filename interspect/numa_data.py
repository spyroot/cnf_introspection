# collects numa related data points
# Mus
import subprocess
import warnings
from pathlib import Path
from typing import List


def numa_topo_data(cmd):
    """Save numa topology and the rest to a svg file.
    :return:
    """
    # --output-format svg topo.svg
    try:
        result = subprocess.run(["lstopo-no-graphics", "--output-format", "svg", "/tmp/topo.svg"],
                                check=True, capture_output=True)
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")


def numa_topo_data_console(cmd):
    """Save numa topology and the rest to a svg file.
    :return:
    """
    try:
        cmdr = subprocess.run(["lstopo-no-graphics", "--no-io", "-P", "--no-caches"],
                              check=True, capture_output=True)
        output = cmdr.stdout.decode()
        print(output)
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")
