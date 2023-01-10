# Network os data collector.
# Mus
import argparse
import os
import subprocess
from pathlib import Path
from typing import List, Optional


def installed(distro_installers: List[Optional]):
    return [Path(p).exists() for p in distro_installers]


def network_time_hw_offload_data(eth_name: str) -> dict:
    """Network adapter time offload capability. 
    :param eth_name:
    :return:
    """
    cmdr = subprocess.run(["ethtool", "-T", eth_name], check=True, capture_output=True)
    decoded = cmdr.stdout.decode().split("\n")[:-1]
    return dict([s.strip().split(":", 1) for s in decoded if len(s) > 0])


def network_adapter_data(eth_name: str) -> dict:
    """Network adapter base data firmware/driver etc
    :param eth_name:
    :return:
    """
    cmdr = subprocess.run(["ethtool", "-i", eth_name], check=True, capture_output=True)
    decoded = cmdr.stdout.decode().split("\n")[:-1]
    return dict([s.strip().split(":", 1) for s in decoded if len(s) > 0])


def network_addr_mac(eth_name: str) -> str:
    """Return network adapter permanent mac address.
    :param eth_name: name eth0 enp7s0 etc
    :return:
    """
    cmdr = subprocess.run(["ethtool", "-P", eth_name], check=True, capture_output=True)
    output = cmdr.stdout.decode()
    if len(output) > 0 and cmdr.returncode == 0:
        return output.split("address:")[1:][0].strip()


def network_adapters_data():
    """

    :return:
    """
    result = subprocess.run(["lshw", "-class", "network", "-businfo"],
                            check=True, capture_output=True)
    if result.returncode != 0:
        print("Failed execute lshw, make sure it installed.")

    network_adapters = {}
    decoded = result.stdout.decode()
    if len(decoded) == 0:
        return {}
    decoded = decoded.split()

    for i in range(0, len(decoded)):
        network_adapter = {}
        if 'pci@' not in decoded[i]:
            continue
        network_adapter['pci'] = decoded[i].split("@")[1:][0]
        eth_name = decoded[i + 1].strip()
        network_adapter["name"] = eth_name
        network_adapter['address'] = network_addr_mac(eth_name)
        network_adapter.update(network_adapter_data(eth_name))
        network_adapter.update(network_time_hw_offload_data(eth_name))
        network_adapters[eth_name] = network_adapter

    return network_adapters


def main():
    """
    :return:
    """
    print(network_adapters_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Network data collector")
    parser.add_argument('--is_verbose', action='store_true', required=False,
                        help="Enable verbose")

    args = parser.parse_args()
    main()

