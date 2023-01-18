import os
import subprocess
from typing import Dict, Tuple
from pathlib import Path


def kernel_name() -> str:
    """Return kernel name. (current active kernel)
    :return:
    """
    cmdr = subprocess.run(["uname", "-r"], check=True, capture_output=True)
    output = cmdr.stdout.decode()
    if len(output) > 0 and cmdr.returncode == 0:
        return output.strip()

    return ""


def kernel_kv(kernel_config_file: str) -> Tuple[Dict, Dict]:
    """Reads kernel config and return two dicts for modules and flags used to compile a kernel
    :return:
    """
    print("Reading file", kernel_config_file)
    translator = str.maketrans({chr(10): '', chr(9): ''})

    kernel_mod = {}
    kernel_config = {}
    try:
        with open(kernel_config_file, 'r', encoding="utf8") as kernel_cfg:
            for line in kernel_cfg:
                if "#" in line.rstrip():
                    continue
                data = line.split("=", 1)
                data = [d.translate(translator) for d in data]
                if len(data) == 2:
                    if data[1] == "n":
                        continue
                    elif data[1] == "m":
                        kernel_mod[data[0].strip()] = data[1].strip()
                    elif data[1] == "y":
                        kernel_config[data[0].strip()] = data[1].strip()
                    else:
                        kernel_config[data[0].strip()] = data[1].strip()
        return kernel_config, kernel_mod
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first. Error: ", fnfe)

    return kernel_config, kernel_mod


def read_kernel_configs():
    """Read all kernel config
    :return:
    """
    kern_configs = {}
    kern_name = kernel_name()
    _configs = [Path("/proc/config.gz"),
                Path("/boot/config-" + kern_name),
                Path("/usr/src/linux-" + kern_name + "/.config"),
                Path("/usr/src/linux/.config")]

    valid_path = {}
    for p in _configs:
        if p.exists() and p.is_file():
            valid_path[p] = True

    # we swap each config is key, if we have more then one caller need check both

    for v in valid_path:
        kern_cfg, ken_mod = kernel_kv(str(v))
        kern_configs[str(v)]['kernel_config'] = kern_cfg
        kern_configs[str(v)]['kernel_modules'] = ken_mod

    return kern_configs
