import os


def mem_info(cmd):
    """Return mem info stats
    :return:
    """
    try:
        if os.path.isfile("/proc/meminfo") and os.access("/proc/meminfo", os.R_OK):
            myfile = open("/proc/meminfo", 'r')
            for line in myfile:
                print
                line.rstrip("\n")
            myfile.close()
    except FileNotFoundError as fnfe:
        print("You need to install lshw and ethtool first.")
