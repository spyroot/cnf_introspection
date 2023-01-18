version: "3.9"
services:
  docker_realtime:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: realtime_docker
    tty: true
    cap_add:
      - SYS_NICE
    ulimits:
      rtprio: 99
      rttime: -1
      memlock: 8428281856
    network_mode: host
    volumes:
      - ../src:/benchmark/src
      - ../test:/benchmark/test
docker run -it --name VCUENO2 --privileged --cap-add=ALL --cpu-rt-runtime=50000 \
--security-opt seccomp=unconfined \
-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
-v /sys/kernel/mm/hugepages/hugepages-2048kB:/sys/kernel/mm/hugepages/hugepages-2048kB \
-v /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages:/sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages \
-v /sys/devices/system/node:/sys/devices/system/node \
-v /dev:/dev \
-d -v /home/cu_data/VCUENO2/db:/enc_data \
-v /home/cu_data/VCUENO2/data:/scw/lvm_mounts \
-v /lib/modules:/lib/modules \
-e MODE=4 \
-e PCI_DEVICE_LIST_DOCKER=0000:01:00.1 \
-e FE_64=1 \
-e FE_NUM_CORES=1 \
-e NUM_HUGEPAGES="40" \
nrdocker_builder_cu_dpdk:latest