import os


def mem_info(cmd):
    """Return mem info stats
    :return:
    """
    data_dict = {}
    try:
        if os.path.isfile("/proc/meminfo") and os.access("/proc/meminfo", os.R_OK):
            proc_mem_fd = open("/proc/meminfo", 'r')
            for line in proc_mem_fd:
                data = line.split(":")
                if len(data) > 0:
                    data_dict[data[0].strip()] = data[1].strio()
            proc_mem_fd.close()
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")

    print(data_dict)
    return data_dict
