#!/usr/bin/env bash

docker start custom-docker-fluent-logger

main_eth_name="eno1"
pci_device="d8"
pci_list_seperator="," # flatten and comma

sriov_nic=ens8f0
num_vfs=64

modprobe vfio-pci enable_sriov=1

interface_status=$(ip link show ens8f0 | grep UP)
[[ -z "$interface_status" ]] && { echo "Error: Interface $sriov_nic either down or invalid."; exit 1; }

pci_utils_ver=$(yum info pciutils | grep -wns Installed -A 2 | grep Version| rev | tr ":" "\n" | rev | awk '{$1=$1};1' | head -n 1)
[[ -z $pci_utils_ver ]] && { echo "Installing pciutils"; yum install pciutils; }

numactl_ver=$(yum info numactl | grep -wns Installed -A 2 | grep Version| rev | tr ":" "\n" | rev | awk '{$1=$1};1' | head -n 1)
[[ -z $numactl_ver ]] && { echo "Installing numactl"; yum install numactl; }

lshw_ver=$(yum info lshw | grep -wns Installed -A 2 | grep Version| rev | tr ":" "\n" | rev | awk '{$1=$1};1' | head -n 1)
[[ -z $lshw_ver ]] && { echo "Installed lshw"; yum install lshw; }

nodes=$(numactl --hardware | grep cpus | tr -cd "[:digit:] \n")
# note this one will give you numa row and col cores.
[[ -z "$nodes" ]] && { echo "Error: numa nodes string empty"; exit 1; }

maddr=$(ip address show $main_eth_name | grep inet | grep brd | awk '{$1=$1};1'|cut -d' ' -f2|cut -d/ -f1)
[[ -z "$maddr" ]] && { echo "Error: ip address string empty"; exit 1; }

vfs_pci_addr=$(lspci | grep $pci_device | grep Virtual | cut -d' ' -f1 | sort -n | sed 's/^/0000:/' | tr -s "\n" $pci_list_seperator | sed 's/.$//')
[[ -z "$vfs_pci_addr" ]] && { echo "Error: vfs pci addr string empty"; exit 1; }

echo $maddr
echo $vfs_pci_addr

sriov_nic=ens8f0
num_vfs=64
num_cur_vfs=$(cat /sys/class/net/$sriov_nic/device/sriov_numvfs)

if [ "$num_vfs" -ne "$num_cur_vfs" ]; then
	echo "Error: Expected number of sriov vfs for adapter $sriov_nic vfs=$num_vfs, found $num_cur_vfs";
	echo $num_vfs >  /sys/class/net/ens8f0/device/sriov_numvfs;
fi