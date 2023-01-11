import subprocess


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


def cpu_interrupts(cmd):
    """Return cpu stats in json
    :return:
    """
    try:
        cmdr = subprocess.run(["mpstat", "-I", "SCPU", "-o", "JSON"], check=True, capture_output=True)
        output = cmdr.stdout.decode()
        return output
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")


def kernel_cmdline(cmd):
    """Save numa topology and the rest to a svg file.
    :return:
    """
    try:
        cmdr = subprocess.run(["cat", "/proc/cmdline"], check=True, capture_output=True)
        output = cmdr.stdout.decode()
        return output
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")
