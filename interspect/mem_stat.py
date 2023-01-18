import os
from typing import Optional
from interspect.cpu_stat import cpu_capability_stats


def mem_stats(is_huge_page_only: Optional[bool] = False):
    """Return mem info stats
    :param is_huge_page_only: will return dict with huge pages only
    :return:
    """
    data_dict = {}
    try:
        if os.path.isfile("/proc/meminfo") and os.access("/proc/meminfo", os.R_OK):
            with open("/proc/meminfo", 'r', encoding="utf8") as proc_mem_fd:
                for line in proc_mem_fd:
                    data = line.split(":")
                    if len(data) > 0:
                        data_dict[data[0].strip()] = data[1].strip()
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first. Error: ", fnfe)

    huge_keys = ["HugePages_Total", "HugePages_Free", "HugePages_Rsvd",
                 "HugePages_Surp", "Hugepagesize", "Hugetlb"]

    if is_huge_page_only:
        data_dict = {key: data_dict[key] for key in huge_keys}

    return data_dict


def mem_large_page(gb_kv='pdpe1gb'):
    """Return dict pdpe1gb true if all CPU support pdpe1gb
    :return:
    """
    data_dict = cpu_capability_stats()
    d = [k['flags'][gb_kv] for k in data_dict.values()]
    return {"pdpe1gb": len(data_dict.keys()) == len(d)}

