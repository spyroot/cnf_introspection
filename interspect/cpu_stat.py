import os
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


def kernel_cmdline() -> Dict:
    """Return current kernel cmd line.
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


def cpu_capability_stats():
    """cpu capability
    :return:
    """
    data_dict = {}
    try:
        if os.path.isfile("/proc/cpuinfo") and os.access("/proc/cpuinfo", os.R_OK):
            proc_mem_fd = open("/proc/cpuinfo", 'r')
            cpu_id = None
            for line in proc_mem_fd:
                data = line.split(":")
                if len(data) > 0 and 'processor' in data[0].strip():
                    cpu_id = data[1].strip()
                    data_dict[cpu_id] = {}
                if len(data) > 0 and cpu_id is not None:
                    data_dict[cpu_id][data[0].strip()] = data[1].strip()

            proc_mem_fd.close()
        return data_dict
    except FileNotFoundError as fnfe:
        print("Failed to access /proc/cpuinfo. Error", fnfe)