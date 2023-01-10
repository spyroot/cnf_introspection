import argparse
import os
from typing import Optional, List

from interspect.network_data import network_adapters_data, installed, run_distro_installer


def run_install_dep(required_apps: Optional[List[str]] = None):
    """Install required packages.
    :return:
    """
    if required_apps is None:
        required_apps = ["lshw", "ethtool"]

    if os.geteuid() != 0:
        print("You need run --install_dep as root.")
        exit(1)

    distro_installers = installed()
    for (is_installed, inst_tool) in distro_installers:
        if is_installed is True:
            # ubuntu specific
            if 'apt' in inst_tool:
                required_apps += ["net-tools"]
            run_distro_installer(inst_tool, required_apps)


def main(cmd):
    """
    :param cmd:
    :return:
    """
    if cmd.install_dep:
        run_install_dep()

    netdata = network_adapters_data(cmd)
    if netdata is not None:
        print(netdata)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Network data collector")
    parser.add_argument('--is_verbose', action='store_true', required=False,
                        help="Enable verbose output.")
    parser.add_argument('--install_dep', action='store_true', required=False,
                        help="Install required tools.")

    args = parser.parse_args()
    main(args)
