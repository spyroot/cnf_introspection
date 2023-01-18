# !/usr/bin/env python
"""
 Main entry for cli tool
 Mus
"""
import os
import argparse
import json
import sys
import yaml
from typing import Optional, List
from interspect.mem_stat import mem_stats, mem_large_page
from interspect.network_data import network_adapters_data, installed, run_distro_installer
from interspect.numa_data import numa_topo_data, numa_topo_data_console
from interspect.cpu_stat import cpu_per_core, kernel_cmdline, cpu_interrupts, cpu_capability_stats
from interspect.vmstats import vm_stat


def nice_json(json_data, sort: Optional[bool] = True, indents: Optional[int] = 4):
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


def nice_yaml(data, default_style: Optional[str] = "plain",
              default_flow_style: Optional[bool] = False,
              encoding: Optional[str] = "utf-8",
              allow_unicode: Optional[bool] = True):
    """Make yaml look nice.
    plain, single-quoted, double-quoted, literal, and folded
    :param data:
    :param default_style:
    :param default_flow_style:
    :param encoding:
    :param allow_unicode:
    :return:
    """
    print(yaml.dump(data, default_style=default_style,
                    default_flow_style=default_flow_style,
                    encoding=encoding,
                    allow_unicode=allow_unicode))


def printer_router(data, is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Main printer router,  dispatch data to correct printer.
    :param data:  python dict or any other data structure that json and yaml should be able to re-present.
    :param is_yaml: if caller asked yaml otherwise default json
    :param is_verbose: will dump raw dict (mainly debug)
    :return:
    """
    if data is None:
        return

    if is_verbose:
        print(data)

    if is_yaml:
        nice_yaml(yaml.dump(data))
    else:
        nice_json(data)


def run_install_dep(required_apps: Optional[List[str]] = None):
    """Installs required packages
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


def memory(hugepages, is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Return memory related stats.
    :param is_yaml: if serialized as yaml
    :param hugepages: Filters and output dict json will store only huge pages data.
    :param is_verbose:
    :return:
    """
    data = mem_stats(is_huge_page_only=bool(hugepages))
    printer_router(data, is_yaml, is_verbose)


def cpu(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Return cpu related stats.
    :param is_yaml: if serialized as yaml
    :param is_verbose:
    :return:
    """
    printer_router(cpu_per_core(), is_yaml=is_yaml, is_verbose=is_verbose)


def cpu_interrupt(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Return interrupts
    :param is_yaml:
    :param is_verbose:
    :return:
    """
    printer_router(cpu_interrupts(), is_yaml=is_yaml, is_verbose=is_verbose)


def numa(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Collect numa topology and other data.
    :param is_yaml: if serialized as yaml
    :param is_verbose:
    :return:
    """
    numa_topo_data_console(None)


def kernel(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Collect kernel loader and flags.
    :param is_yaml: if serialized as yaml
    :param is_verbose:
    :return:
    """
    printer_router(kernel_cmdline(), is_yaml=is_yaml, is_verbose=is_verbose)


def network(interface: str, pci: str, mac_addr: str,
            is_yaml: Optional[bool] = False,
            is_verbose: Optional[bool] = False) -> None:
    """Network command
    :param interface:  Filter by interface name
    :param pci: Filter by pci address
    :param mac_addr:  Filter by mac address
    :param is_verbose:
    :param is_yaml: if serialized as yaml
    :return: None
    """
    netdata = network_adapters_data(interface=interface, pci_addr=pci, mac_addr=mac_addr)
    if netdata is not None:
        printer_router(netdata, is_yaml=is_yaml, is_verbose=is_verbose)


def cpu_capability(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Collect cpu capability
    :return:
    """
    printer_router(cpu_capability_stats(), is_yaml=is_yaml, is_verbose=is_verbose)


def large_huge(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Return dict if system support 1G Huge pages.
    :return:
    """
    printer_router(large_huge(), is_yaml=is_yaml, is_verbose=is_verbose)


def vmstat(is_yaml: Optional[bool] = False, is_verbose: Optional[bool] = False):
    """Return vm_stat json cmd
    :return:
    """
    printer_router(vm_stat(), is_yaml=is_yaml, is_verbose=is_verbose)


def install_dep():
    """
    :return:
    """
    print("Run install dep")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CNF worker node data collector.")
    parser.add_argument('--is_verbose', action='store_true', required=False,
                        help="Enable verbose output.")
    parser.add_argument('--yaml', action='store_true', required=False, dest="is_yaml",
                        help="Changes output from json to yaml.")

    parser.add_argument('--install_dep', action='store_true', required=False, dest="install_dep",
                        help="Install required tools and packages.")

    subparsers = parser.add_subparsers(dest='subparser')

    parser_a = subparsers.add_parser('memory')
    parser_a.add_argument('--hugepages', dest='hugepages',
                          action='store_true', required=False, help='hugepages.')

    cpu_cmd = subparsers.add_parser('network', help="collect network related data")
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
        kwargs.pop('install_dep')
        globals()[kwargs.pop('subparser')](**kwargs)
