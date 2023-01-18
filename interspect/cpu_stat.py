import subprocess
from typing import Dict


def cpu_per_core(cmd):
    """Return cpu stats in json
    :return:
    """
    try:
        cmdr = subprocess.run(["mpstat", "-P", "ALL", "-o", "JSON"], check=True, capture_output=True)
        output = cmdr.stdout.decode()
        return output
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")


def cpu_interrupts():
    """Return cpu interrupts stats serialized as a json
    :return:
    """
    try:
        cmdr = subprocess.run(["mpstat", "-I", "SCPU", "-o", "JSON"], check=True, capture_output=True)
        decoded = cmdr.stdout.decode()
        return decoded
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")


def kernel_cmdline(cmd) -> Dict:
    """Return current kernel cmd line
    :return: dict
    """
    try:
        cmdr = subprocess.run(["cat", "/proc/cmdline"], check=True, capture_output=True)
        decoded = cmdr.stdout.decode().strip()
        decoded = set(decoded.split(" "))
        data = dict.fromkeys(decoded, True)
        return data
    except FileNotFoundError as fnfe:
        print("You need to install cat.")