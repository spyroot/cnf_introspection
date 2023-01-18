import os
import subprocess
from typing import Dict

def vmstat():
    """Return vmstats info stats
    :return:
    """
    data_dict = {}
    try:
        if os.path.isfile("/proc/vmstat") and os.access("/proc/vmstat", os.R_OK):
            with open("/proc/vmstat", 'r', encoding="utf8") as proc_mem_fd:
                for line in proc_mem_fd:
                    data = line.split(" ")
                    if len(data) > 0:
                        data_dict[data[0].strip()] = data[1].strip()
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first. Error: ", fnfe)

    return data_dict
