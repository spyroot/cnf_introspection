# Numa data
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
    # --output-format svg topo.svg
    try:
        result = subprocess.run(["lstopo-no-graphics",
                                 "--output-format", "svg", "/tmp/topo.svg"],
                                check=True, capture_output=True)
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")
