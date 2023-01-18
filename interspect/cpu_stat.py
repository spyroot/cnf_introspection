"""cpu related data
 Mus
"""
import os
import subprocess
from typing import Dict


def cpu_per_core():
    """Return cpu stats in json
    :return:
    """
    try:
        cmdr = subprocess.run(["mpstat", "-P", "ALL", "-o", "JSON"], check=True, capture_output=True)
        output = cmdr.stdout.decode()
        return output
    except FileNotFoundError as _:
        print("You need to install lshw and ethtool first.")
    return {}


def cpu_interrupts():
    """Return cpu interrupts stats serialized as a json
    :return: dict
    """
    try:
        cmdr = subprocess.run(["mpstat", "-I", "SCPU", "-o", "JSON"], check=True, capture_output=True)
        decoded = cmdr.stdout.decode()
        return decoded
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.  Error:", fnfe)
    return {}


def kernel_cmdline() -> Dict:
    """Return current kernel cmd line.
    :return: dict
    """
    kernel_cmd = {}
    try:
        cmdr = subprocess.run(["cat", "/proc/cmdline"], check=True, capture_output=True)
        decoded = cmdr.stdout.decode().strip()
        decoded = set(decoded.split(" "))
        for d in decoded:
            if '=' in d:
                data = d.split('=')
                if data is not None and len(data) == 2:
                    kernel_cmd[data[0]] = data[1]
            else:
                kernel_cmd[d] = True
        # data = dict.fromkeys(decoded, True)
        return kernel_cmd
    except FileNotFoundError as fnfe:
        print("You need to install cat. Error", fnfe)

    return kernel_cmd


def cpu_capability_stats():
    """Returns cpu capability.
    :return:
    """
    data_dict = {}
    try:
        if os.path.isfile("/proc/cpuinfo") and os.access("/proc/cpuinfo", os.R_OK):
            with open("/proc/cpuinfo", 'r', encoding="utf8") as proc_mem_fd:
                cpu_id = None
                for line in proc_mem_fd:
                    data = line.split(":")
                    if data is not None and len(data) == 2:
                        data_key = data[0].strip()
                        data_value = data[1].strip()
                        if 'processor' in data_key and len(data_key) > 0:
                            cpu_id = data_value
                            data_dict[cpu_id] = {}
                            data_dict[cpu_id]['processor'] = data_value
                        else:
                            if 'flags' == data_key or 'vmx flags' == data_key or 'bugs' == data_key:
                                data_dict[cpu_id][data_key] = dict.fromkeys(data_value.split(), True)
                            else:
                                data_dict[cpu_id][data_key] = data_value
        return data_dict
    except FileNotFoundError as fnfe:
        print("Failed to access /proc/cpuinfo. Error", fnfe)

    return {}
