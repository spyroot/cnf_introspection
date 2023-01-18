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


def main(cmd):
    """Main entry
    :param cmd: args
    :return:
    """
    print(cmd)
    print(cmd.memory)
    print(cmd.hugepages)

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
    parser = argparse.ArgumentParser(description="CNF worker node data collector.")
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
    # parser.add_argument('--memory', action='store_true', required=False,
    #                     help="memory details.")

    parser.add_argument('--all', action='store_true', required=False,
                        help="kernel details.")
    parser.add_argument('--install_dep', action='store_true', required=False,
                        help="Install required tools.")

    sub_memory = parser.add_subparsers(help='memory related sub-commands')
    parser_huge_page = sub_memory.add_parser('--memory', help="memory only")
    parser_huge_page.add_argument('--hugepages', action='store_true', required=False, help='return only hugepages')

    args = parser.parse_args()
    main(args)
