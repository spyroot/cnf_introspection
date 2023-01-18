import os
import subprocess
import warnings
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


def list_kernel_mods() -> Dict[str, bool]:
    """Return list of kernel modules,  if module not in use value for a key False.
    :return:
    """
    kern_modules = {}
    decoded = None
    cmdr_ret = -1
    try:
        cmdr = subprocess.run(["lsmod"], check=True, capture_output=True)
        cmdr_ret = cmdr.returncode
        decoded = cmdr.stdout.decode()
    except FileNotFoundError as fnfe:
        print("You need to install lsmod or adjust $PATH. Error: ", fnfe)

    if decoded is not None and len(decoded) > 0 and cmdr_ret == 0:
        decoded = decoded.split("\n")[1:]
        for decoded_line in decoded:
            decoded_line = decoded_line.strip().split()
            if decoded_line is None or len(decoded_line) < 2:
                continue
            translator = str.maketrans({chr(10): '', chr(9): ''})
            decoded_line = [d.translate(translator) for d in decoded_line]
            try:
                mod_name = decoded_line[0].strip()
                mod_in_use = decoded_line[2].strip()
                if len(mod_name) > 0 and len(mod_in_use):
                    inuse = int(mod_in_use)
                    kern_modules[mod_name] = True if inuse > 0 else False
            except ValueError as ve:
                warnings.warn(f"Failed decoded line. Error {str(ve)}")

    return kern_modules


def kernel_kv(kernel_config_file: str) -> Tuple[Dict, Dict]:
    """Reads kernel config and return two dicts for modules and flags used to compile a kernel
    :return:
    """
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
    found_at_least_one = False
    for p in _configs:
        if p.exists() and p.is_file():
            valid_path[p] = True
            found_at_least_one = True

    if found_at_least_one is False:
        print("Failed locate kernel config.")
        return {}
    # we swap each config is key, if we have more then one caller need check both

    for v in valid_path:
        kern_configs[str(v)] = {}
        kern_cfg, ken_mod = kernel_kv(str(v))
        kern_configs[str(v)]['kernel_config'] = kern_cfg
        kern_configs[str(v)]['kernel_modules'] = ken_mod

    return kern_configs
