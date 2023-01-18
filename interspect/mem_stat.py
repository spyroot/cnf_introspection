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
                data = line.split(":")[1:][0].strip()
                print(data)
            proc_mem_fd.close()
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")
