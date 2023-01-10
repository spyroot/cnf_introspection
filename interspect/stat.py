import subprocess


def cpu_per_core(cmd, times=1):
    """Save numa topology and the rest to a svg file.
    :return:
    """
    # --output-format svg topo.svg
    try:
        result = subprocess.run(["sar",
                                 "-P", "ALL", 1, times],
                                check=True, capture_output=True)
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")
