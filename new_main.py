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
from interspect.mem_stat import mem_stats, mem_large_page
from interspect.network_data import network_adapters_data, installed, run_distro_installer
from interspect.numa_data import numa_topo_data, numa_topo_data_console
from interspect.cpu_stat import cpu_per_core, kernel_cmdline, cpu_interrupts, cpu_capability_stats


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


def memory(hugepages, is_verbose: bool):
    """Return memory stats
    :param hugepages: Filters and output dict json will store only huge pages data.
    :param is_verbose:
    :return:
    """
    nice_json(mem_stats(is_huge_page_only=bool(hugepages)))


def cpu(is_verbose: bool):
    """
    :return:
    """
    nice_json(cpu_per_core(None))


def cpu_interrupt(is_verbose: bool):
    """Return interrupts
    :param is_verbose:
    :return:
    """
    nice_json(cpu_interrupts())


def numa(is_verbose: bool):
    """
    :param is_verbose:
    :return:
    """
    numa_topo_data_console(None)


def kernel(is_verbose: bool):
    """
    :param is_verbose:
    :return:
    """
    nice_json(kernel_cmdline())


def network(interface: str, pci: str, mac_addr: str, is_verbose: Optional[bool] = False):
    """Network command
    :param interface:  Filter by interface name
    :param pci: Filter by pci address
    :param mac_addr:  Filter by mac address
    :param is_verbose:
    :return: json
    """
    netdata = network_adapters_data(interface=interface, pci_addr=pci, mac_addr=mac_addr)
    if netdata is not None:
        nice_json(netdata)


def cpu_capability(is_verbose: bool):
    """
    :return:
    """
    nice_json(cpu_capability_stats())


def large_huge(is_verbose: bool):
    """Return dict if system support 1G Huge pages.
    :return:
    """
    nice_json(mem_large_page())


def vmstat(is_verbose: bool):
    """vmstat cmd
    :return:
    """
    nice_json(mem_large_page())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CNF worker node data collector.")
    parser.add_argument('--is_verbose', action='store_true', required=False,
                        help="Enable verbose output.")

    subparsers = parser.add_subparsers(dest='subparser')

    parser_a = subparsers.add_parser('memory')
    parser_a.add_argument('--hugepages', dest='hugepages',
                          action='store_true', required=False, help='hugepages.')

    cpu_cmd = subparsers.add_parser('network')
    cpu_cmd.add_argument('-i', '--interface', dest='interface', default="",
                         help="Filter by interface  name eth0 etc.")
    cpu_cmd.add_argument('-p', '--pci', dest='pci', default="",
                         help="Filter by pci address 0000:5e:00.1.")
    cpu_cmd.add_argument('-m', '--mac_addr', dest='mac_addr', default="",
                         help="Filter by mac address address 98:03:9b:b9:a4:8b.")

    cpu_cmd = subparsers.add_parser('cpu')
    numa_cmd = subparsers.add_parser('numa')
    kernel_cmd = subparsers.add_parser('kernel')
    cpu_interrupt_cmd = subparsers.add_parser('cpu_interrupt')
    cpu_cap_cmd = subparsers.add_parser('cpu_capability')
    large_page_cmd = subparsers.add_parser('large_huge')
    vmstat_cmd = subparsers.add_parser('vmstat')

    kwargs = vars(parser.parse_args())
    if kwargs['subparser'] is not None:
        globals()[kwargs.pop('subparser')](**kwargs)
