import os
from optparse import Option


def mem_info(cmd, is_huge_page_only: Option[bool] = False):
    """
    Return mem info stats
    :param cmd:
    :param is_huge_page_only: will return dict with huge pages only
    :return:
    """
    data_dict = {}
    try:
        if os.path.isfile("/proc/meminfo") and os.access("/proc/meminfo", os.R_OK):
            proc_mem_fd = open("/proc/meminfo", 'r')
            for line in proc_mem_fd:
                data = line.split(":")
                if len(data) > 0:
                    data_dict[data[0].strip()] = data[1].strip()
            proc_mem_fd.close()
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")

    huge_keys = ["HugePages_Total", "HugePages_Free", "HugePages_Rsvd",
                 "HugePages_Surp", "Hugepagesize", "Hugetlb"]
    if is_huge_page_only:
        data_dict = {key: data_dict[key] for key in huge_keys}

    return data_dict
