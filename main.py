#!/usr/bin/env python
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


def main(cmd):
    """Main entry
    :param cmd: args
    :return:
    """
    if cmd.install_dep:
        run_install_dep()

    if cmd.network:
        netdata = network_adapters_data(cmd)
        if netdata is not None:
            nice_json(netdata)

    if cmd.numa or cmd.all:
        numa_topo_data_console(cmd)
    if cmd.cpu or cmd.all:
        nice_json(cpu_per_core(cmd))
    if cmd.cpu_interrupt or cmd.all:
        nice_json(cpu_interrupts(cmd))
    if cmd.kernel or cmd.all:
        nice_json(kernel_cmdline(cmd))
    if cmd.memory or cmd.all:
        nice_json(mem_info(cmd))


if __name__ == '__main__':
    """
    """
    parser = argparse.ArgumentParser(description="Network data collector")
    parser.add_argument('--is_verbose', action='store_true', required=False,
                        help="Enable verbose output.")
    parser.add_argument('--network', action='store_true', required=False,
                        help="network details.")
    parser.add_argument('--cpu', action='store_true', required=False,
                        help="view cpu stats details.")
    parser.add_argument('--cpu_interrupt', action='store_true', required=False,
                        help="view cpu stats details.")
    parser.add_argument('--numa', action='store_true', required=False,
                        help="view numa details.")
    parser.add_argument('--kernel', action='store_true', required=False,
                        help="kernel details.")
    parser.add_argument('--memory', action='store_true', required=False,
                        help="memory details.")

    sub_memory = parser.add_subparsers(help='memory help')
    parser_huge_page = sub_memory.add_parser('hugepage', help='huge pages only.')

    parser.add_argument('--all', action='store_true', required=False,
                        help="kernel details.")
    parser.add_argument('--install_dep', action='store_true', required=False,
                        help="Install required tools.")

    args = parser.parse_args()
    main(args)
