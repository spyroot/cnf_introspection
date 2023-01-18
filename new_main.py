import argparse
from typing import Optional

# !/usr/bin/env python
"""
 Main entry for cli tool
 Mus
"""
import os
import argparse
import json
import sys
from typing import Optional, List
from interspect.mem_stat import mem_info
from interspect.network_data import network_adapters_data, installed, run_distro_installer
from interspect.numa_data import numa_topo_data, numa_topo_data_console
from interspect.cpu_stat import cpu_per_core, kernel_cmdline, cpu_interrupts

def nice_json(json_data: str, sort: Optional[bool] = True, indents: Optional[int] = 4):
    """Make json look nice.
    :param json_data:
    :param sort:
    :param indents:
    :return:
    """
    if isinstance(json_data, str):
        print(json.dumps(json.loads(json_data), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_data, sort_keys=sort, indent=indents))


def run_install_dep(required_apps: Optional[List[str]] = None):
    """Install required packages.
    :return:
    """
    # default list required
    if required_apps is None:
        required_apps = ["lshw", "ethtool", "hwloc"]

    if os.geteuid() != 0:
        print("You need to run --install_dep as root.")
        sys.exit(1)

    distro_installers = installed()
    for (is_installed, inst_tool) in distro_installers:
        if is_installed is True:
            # ubuntu specific
            if 'apt' in inst_tool:
                required_apps += ["net-tools", "build-essential", "libnuma-dev"]
            run_distro_installer(inst_tool, required_apps)


def memory(hugepages, is_verbose):
    print('task a', hugepages)


def cpu(beta, gamma):
    print('task b', beta, gamma)


def cpu_interrupt():
    print('task interupts')


def numa():
    print('task numa')


def kernel():
    print('task cpu')


def network(interface: str, pci: str, is_verbose: Optional[bool] = False):
    """

    :param interface:
    :param pci:
    :param is_verbose:
    :return:
    """
    print('task interface, filter interface name', interface)
    print('task interface filter pci addr', pci)
    netdata = network_adapters_data(interface=interface, pci_addr=pci)
    if netdata is not None:
        nice_json(netdata)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CNF worker node data collector.")
    parser.add_argument('--is_verbose', action='store_true', required=False,
                        help="Enable verbose output.")

    subparsers = parser.add_subparsers(dest='subparser')

    parser_a = subparsers.add_parser('memory')
    parser_a.add_argument('--hugepages', dest='hugepages',
                          action='store_true', required=False, help='hugepages.')

    cpu_cmd = subparsers.add_parser('network')
    cpu_cmd.add_argument('-i', '--interface', dest='interface', default="", help='Beta description')
    cpu_cmd.add_argument('-p', '--pci', dest='pci', default="", help='Gamma description')

    cpu_cmd = subparsers.add_parser('cpu')
    numa_cmd = subparsers.add_parser('numa')
    kernel_cmd = subparsers.add_parser('kernel')
    cpu_interrupt_cmd = subparsers.add_parser('cpu_interrupt')

    kwargs = vars(parser.parse_args())
    if kwargs['subparser'] is not None:
        globals()[kwargs.pop('subparser')](**kwargs)
