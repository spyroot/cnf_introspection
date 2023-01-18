#!/usr/bin/env sh
set -x
umask 0022

source /root/vm-scripts/sm_nics.sh #Mention the each NICs PCI addr in sm_nics.sh

# not everyone should be builder
#nrdockerimage=nrdocker_hebbarv #if you are using developer images use this my chnaging the name accordingly
nrdockerimage=nrdocker_builder  #if you are using rel images please use this

# we should transiton to using the actual version
nrdockerversion=latest

XU_NAME="CU-SUB6"
XU_NIC_LIST="${enp138s6},${enp138s6f1}" # 2 VFs from the PF to whihc CU is connected

##Creating the PV
CUDATA_BASE_DIR="/cu_data"

SCW_DB_VOL="$CUDATA_BASE_DIR/$XU_NAME/db"
SCW_DATA_VOL="$CUDATA_BASE_DIR/$XU_NAME/data"
mkdir -p $SCW_DB_VOL
mkdir -p $SCW_DATA_VOL
##


#should be divisble by 5
hostportfordebug=36000

ws_root=""
## NEXT POINT OF INTEREST WOULD BE AROUND LINE 540 ( if [ "x$1" == "x4" ] || [ "x$1" == "x9" ] ONWARDS WHIHC HAS THE docker run command)


function precheck() {
    #Check whether hostportfordebug is even or not
    [ ! $((hostportfordebug%5)) -eq 0 ] && echo "host port should be divisble by 5  " && exit 1
}


container_port_gdb_server=5000

function usage() {
    echo ""
    echo "Usage ::"
    echo "NOTE:::"
    echo "IMP::this script really, really, wants to be run from the directoy it is in.."
    echo ""
    echo "-h|--help                                                     :: Help"
    echo "-b|--build_docker_image <ws root>                             :: Build docker image. This is the default action. Do not use with --buildtype"
    echo "                                                          NOTE:: 'ws root' path is optional, workspace path will be determined if omitted"
    echo "--buildtype <developer|test|release>                          :: Type of build, workspace path will be determined based on the location of this script"
    echo "                                                          NOTE:: Do not use --buildtype with -b"
    echo "-e|--build_docker_image_existing_tar                          :: Build docker image from existing tar"
    echo "-g|--gdb_server_start  <process_name>                         :: Attach gdbserver on a process for living debugging from host"
    echo "-i|--interactive_shell                                        :: Get interactive bash shell for the docker container"
    echo "-m|--mount_workspace                                          :: Mount workspace inside docker container for gdb"
    echo "                                                          NOTE:: Please make sure this option is given before -r"
    echo "-p|--prepare_tar <ws root>                                    :: Prepare tar from root of workspace"
    echo "-u|--update_process  <host_process_path>                      :: Update the process on running docker instance"
    echo "-l|--log                                                      :: Listen to log"
    echo "-r|--run_docker                                               :: Run docker container"
    echo "-s|--stop                                                     :: Stop the running docker"
    echo "-c|--cleanup <sudo ./client.sh -c>                            :: To remove old images and container"
    echo "-t|--type <1:standalone 2:full 3:CU 4:CU_dpdk(default)        :: Type of set (deprecated), you do not need to provide this parameter"
    echo "           5:DU_sim 6:DU_fe>                                  :: "
    # echo "                                                          NOTE:: Used in conjunction with other options. So use it as first command if other than default value"
    echo ""
    echo "Example: $filename $0"
    echo "         $filename $0 --buildtype=test"
    echo ""

}

function cleanup() {
    docker ps -a  | grep Exited  | awk '{print $1}' | xargs docker rm -f 2>/dev/null
    echo "Exited container removed...."
    docker images  -a | grep none  | awk '{print $3}' | xargs docker rmi -f 2>/dev/null
    #docker images -aq | xargs docker rmi -f
    echo "Unused images removed...."

    docker volume prune -f
    #this command will cleanup overlay, so image creation will download/create each layer
    #docker system prune -a -f

    #do the cleanup in overlay, this should recover most of the space
<<COMP
    #Little risky way to do cleanup. Lets wait
    cd /var/lib/docker/overlay2/
    for i in `ls | xargs -I {}  du -shx {}  | grep [1-9][1-9][1-9]M`; do rm -rf $i; done
    for i in `ls | xargs -I {}  du -shx {}  | grep G`; do rm -rf $i; done
COMP
}

function get_container_ip() {
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $1
}

function get_container_process_path() {
    echo "$(docker exec -it  $(get_container_id $1) find / -name $2)"
}

function get_host_port_log() {
    SETUP=$1
    echo $(($hostportfordebug + $SETUP - 1))
}

function get_host_port_gdb() {
    echo $(($hostportfordebug + $SETUP ))
}

function get_container_process_id() {
    echo "`docker exec $1  ps| grep $2| awk '{print $1}'`"
}

#Tries to look for a docker container from the name of the image(set in env.sh)
#and then from the host port imported for debug service (set in env.sh)
function get_container_id() {
    docker_image=`get_docker_image_name $1`
    host_port=`get_host_port_log $1`
    cont_name=`docker ps | grep $docker_image| awk '{print $1}'`
    if [ -z "$cont_name" ]
    then
        cont_name=`docker ps | grep $host_port| awk '{print $1}'`
    fi
    echo $cont_name
}


function interactive_shell() {
    SETUP=$1
    cont_name=$(get_container_id $SETUP)
    echo "docker exec -it $cont_name  bash"
    docker exec -it $cont_name  bash

}
function gdb_server_start() {
    SETUP=$1
    PRC_NAME=$2
    cont_name=$(get_container_id $SETUP)
    host_port_gdb=$(get_host_port_gdb)
    host_ip=$(hostname --ip-address)

    echo "$1    $2   $3"
    prc_path_container=$(get_container_process_path $SETUP $PRC_NAME)

    if [ -z "$prc_path_container" ]
    then
        echo "Could not found PRC:[$PRC_NAME] in container"
        exit 1
    fi
    prc_pid=`get_container_process_id $cont_name $PRC_NAME`
    echo "Container path PRC:[$PRC_NAME]:${prc_path_container}:${prc_pid}."
    echo "docker exec -i -t=false $cont_name gdbserver :$container_port_gdb_server --attach $prc_pid &"

    #Start the gdbserver on the process
    docker exec -i -t=false $cont_name gdbserver :$container_port_gdb_server --attach $prc_pid &

    sleep 2
    echo ""
    echo "ContainerPort[$container_port_gdb_server] HostPort[$host_port_gdb] HostIp[$(host_ip)] for remote gdb debugging"
    echo "Sample comamand to connect to gdbserver :: "
    echo "gdb  -ex 'set solib-search-path /.amd/tees/a/users/pupadhyay/5G_dev/5g_fns/install/x86.linux/lib'  -ex 'directory /.amd/tees/a/users/pupadhyay/5G_dev/5g_fns' -ex 'target remote $host_ip:$host_port_gdb' ./install/x86.linux/bin/nrpdcp "
}


function update_process() {
    SETUP=$1
    HOST_PATH=$2
    cont_name=`get_container_id $SETUP`
    if [ -z "$cont_name" ]
    then
        echo "No container running"
        exit
    fi

    file_name=${HOST_PATH##*/}
    file_dir=`dirname $HOST_PATH}`
    file_path_container=$(get_container_process_path $SETUP $file_name)
    if [ -z "$file_path_container" ]
    then
        echo "File:$file_name not found in container. Will place at root /"
        file_path_container="/$file_name"
    fi
    dir_path_container=`dirname $file_path_container`
    echo "File:$file_name From:$file_dir To:$cont_name::$dir_path_container"
    docker cp $HOST_PATH $cont_name:$dir_path_container

    #Lets kill the process
    # SETUP = 1 ::
    # SETUP = 2 :: procmgr should restart the process
    sudo docker top $cont_name | grep $file_name | awk '{print $2}' | xargs kill -9

    echo "Return status :: $?"
    echo "Process $file_name killed in container[$cont_name]"
}


function prepare_tar() {
    WS_PATH=$1
    SETUP=$2
#array of file list. Format : <Source Dir/File>:<Destination Directory>
    standalone_file_list=(/volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib:platform/gcc
	platform/install/x86.linux/bin:platform
	platform/install/x86.linux/lib:platform
	platform/install/x86.linux/vendor/lib:platform/vendor
	5g_fns/install/x86.linux/bin:nr
	5g_fns/install/x86.linux/lib:nr
	ws_common/install/x86.linux/lib:ws_common)

    full_file_list=(${pkg_dir}/x86_release/x86*[0-9]:packages
	/opt//volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib:packages
	5g_fns/install/x86.linux/bin:packages/nr
	5g_fns/install/x86.linux/lib:packages/nr
	ws_common/install/x86.linux/lib:packages/ws_common)

    cu_file_list=(${pkg_dir}/x86_CU_release/x86*[0-9]:packages
	5g_fns/install/x86.linux/bin/nr_cellagt:packages/nr
	5g_fns/install/x86.linux/scripts/cellmgrdb.ini:packages/nr
	platform/install/x86_64.linux/scripts/sc_boot.sh:scripts
	/volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib:packages
	/volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib64:packages
)

    cu_appliance_file_list=(${pkg_dir}/x86_CU_appliance_release/x86*[0-9]:packages
	    5g_fns/install/x86.linux/bin/nr_cellagt:packages/nr
	    5g_fns/install/x86.linux/scripts/cellmgrdb.ini:packages/nr
	    platform/install/x86_64.linux/scripts/sc_boot.sh:scripts
	    /volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib:packages
	    /volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib64:packages
    )

    du_file_list=(${pkg_dir}/x86_DU_release/x86*[0-9]:packages
	    5g_fns/install/x86.linux/bin/nr_cellagt:packages/nr
	    5g_fns/install/x86.linux/scripts/cellmgrdb.ini:packages/nr
	    vendor-pkg/flexran-21.03-l1app-x86_64.linux.tgz:packages/nr
	    vendor-pkg/flexran-21.03-wls-x86_64.linux.tgz:packages/nr
	    vendor-pkg/icc-19.3.206-libs-x86_64.linux.tgz:packages/nr
	    platform/install/x86_64.linux/scripts/sc_boot.sh:scripts
	    /volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib:packages
	    /volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib64:packages
    )

    mmwrnsim_file_list=(${pkg_dir}/x86_MMWRNSIM_release/x86*[0-9]:packages
	5g_fns/install/x86.linux/bin/nr_cellagt:packages/nr
	5g_fns/install/x86.linux/scripts/cellmgrdb.ini:packages/nr
        platform/install/x86_64.linux/scripts/sc_boot.sh:scripts
	/volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib:packages
	/volume/tools/x86_64_linux.x86_64/5.4.0/x86_64-pc-linux-gnu/x86_64-pc-linux-gnu/sysroot/lib64:packages
 )
    dsim_file_list=(5g_fns/install/x86_64.linux/lib:nr
    platform/install/x86_64.linux/lib:platform/x86_64
    platform/install/x86.linux/lib:platform/x86
    platform/install/x86.linux/bin/siconf:platform/bin
    platform/install/x86_64_fe.linux/vendor/intel-ipsec-mb/lib:platform/vendor
    5g_fns/install/x86_64.linux/bin/datasim:nr/bin
    5g_fns/src/cu/nr_pdcp/datasim/config/conf.ini:nr/config
    5g_fns/src/cu/nr_pdcp/datasim/config/client.sh:nr/config
    5g_fns/src/cu/nr_pdcp/datasim/automation/ds_iperf.py:nr/config
    5g_fns/src/cu/nr_pdcp/datasim/automation/ds_iperf_parse.py:nr/config
    5g_fns/src/cu/nr_pdcp/datasim/automation/ds_iperf3_parse.py:nr/config
)


    file_list=()
    tar_suffix=""
    chmod -R a+w del 2>/dev/null
    rm -rf del || true

    if [ "x$SETUP" == "x2" ]
    then
        file_list=${full_file_list[@]}
        echo "Preparing full setup"
        mkdir -p del/packages
        tar_suffix="_full"
    elif [ "x$SETUP" == "x3" ]
    then
        file_list=${cu_file_list[@]}
        echo "Preparing CU setup"
        mkdir -p del/packages
        mkdir -p del/packages/nr
        tar_suffix="_cu"
    elif [ "x$SETUP" == "x4" ]
    then
        file_list=${cu_file_list[@]}
        echo "Preparing CU setup"
        mkdir -p del/packages
        mkdir -p del/packages/nr
        mkdir -p del/scripts
        tar_suffix="_cu_dpdk"
    elif [ "x$SETUP" == "x5" ]
    then
        file_list=${du_file_list[@]}
        echo "Preparing DU setup"
        mkdir -p del/packages
        mkdir -p del/packages/nr
        mkdir -p del/scripts
        tar_suffix="_du_dpdk"
    elif [ "x$SETUP" == "x6" ]
    then
        file_list=${du_file_list[@]}
        echo "Preparing DU setup"
        mkdir -p del/packages
        mkdir -p del/packages/nr
        mkdir -p del/scripts
        tar_suffix="_du_dpdk"
    elif [ "x$SETUP" == "x7" ]
    then
        file_list=${dsim_file_list[@]}
        echo "Preparing Datasim setup"
        mkdir -p del/platform/x86_64/lib
        mkdir -p del/platform/x86/lib
        mkdir -p del/platform/bin
        mkdir -p del/platform/vendor/lib
        mkdir -p del/nr/lib
        mkdir -p del/nr/bin
        mkdir -p del/nr/config
        tar_suffix="_dsim"
    elif [ "x$SETUP" == "x8" ]
    then
        file_list=${mmwrnsim_file_list[@]}
        echo "Preparing mmw-RNSIM setup"
        mkdir -p del/packages
        mkdir -p del/packages/nr
        mkdir -p del/scripts
        tar_suffix="_mmwrnsim_dpdk"
    elif [ "x$SETUP" == "x9" ]
    then
        file_list=${cu_appliance_file_list[@]}
        echo "Preparing CU setup"
        mkdir -p del/packages
        mkdir -p del/packages/nr
        mkdir -p del/scripts
        touch del/scripts/appliance
        tar_suffix="_cu_dpdk"
    else
        file_list=${standalone_file_list[@]}
        echo "Preparing standalone setup"
        mkdir -p del/platform/vendor
        mkdir -p del/nr
        mkdir -p del/ws_common
        mkdir -p del/platform/gcc
        tar_suffix="_sa"
    fi

    echo ${file_list[*]}
    for file in ${file_list[@]}
    do
        from=`echo $file | cut -d: -f1`
        to=`echo $file | cut -d: -f2`
        #echo "From:$from To:$to"
        #Absoluet Path
        if [[ "$from" = /* ]]
        then
            echo "cp -r $from ./del/$to/"
            cp -r $from ./del/$to/
        else
            echo "cp -r $WS_PATH/$from ./del/$to/"
            cp -r $WS_PATH/$from ./del/$to/
        fi
        echo ""
    done

    cd del

    to_dir=$(dirname "$0")

    #Hack for preparing setup from workspace itself
    if [ "x$to_dir" == "x." ]
    then
        to_dir=../
    fi

    echo "Packaging necessary files @$to_dir"
    rm -f $to_dir/pkg${tar_suffix}.tgz
    tar -zcvf $to_dir/pkg${tar_suffix}.tgz  .
    echo "Package created for docker image @ $to_dir/pkg${tar_suffix}.tgz"
    cd ../
    chmod -R a+w del
    rm -rf del

}

function get_docker_image_name() {
    if [ "x$1" == "x1" ]
    then
        echo ${nrdockerimage}_sa:$nrdockerversion
    elif [ "x$1" == "x2" ]
    then
        echo ${nrdockerimage}_full:$nrdockerversion
    elif [ "x$1" == "x3" ]
    then
        echo ${nrdockerimage}_cu:$nrdockerversion
    elif [ "x$1" == "x4" ]
    then
        echo ${nrdockerimage}_cu_dpdk:$nrdockerversion
    elif [ "x$1" == "x5" ]
    then
        echo ${nrdockerimage}_du_dpdk:$nrdockerversion
    elif [ "x$1" == "x6" ]
    then
        echo ${nrdockerimage}_du_dpdk:$nrdockerversion
    elif [ "x$1" == "x7" ]
    then
        echo ${nrdockerimage}_dsim:$nrdockerversion
    elif [ "x$1" == "x8" ]
    then
        echo ${nrdockerimage}_mmwrnsim_dpdk:$nrdockerversion
    elif [ "x$1" == "x9" ]
    then
        echo ${nrdockerimage}_cu_appliance_dpdk:$nrdockerversion
    fi

}

function build_docker_image() {
    docker_image=`get_docker_image_name $1`
    echo "Building docker image $docker_image from:$PWD"
    if [ "x$1" == "x1" ]
    then
        ./docker_img.sh  -f Dockerfile.standalone  -t $docker_image -n $image_name || exit 1
    elif [ "x$1" == "x2" ]
    then
        docker build . -f Dockerfile.full  -t $docker_image || exit 1
    elif [ "x$1" == "x3" ]
    then
        ./docker_img.sh  -f Dockerfile.cu -t $docker_image || exit 1
    elif [ "x$1" == "x4" ] || [ "x$1" == "x9" ]
    then
        ./docker_img.sh  -f Dockerfile.cu_dpdk -t $docker_image -n $image_name || exit 1
        chmod a+r ${image_name}_docker.img
        mv -b -f ${image_name}_docker.img $package_dir || exit 1
    elif [ "x$1" == "x5" ]
    then
        ./docker_img.sh -f Dockerfile.du_dpdk -t $docker_image -n $image_name
        chmod a+r ${image_name}_docker.img
        mv -b -f ${image_name}_docker.img $package_dir || exit 1
        echo "Image available at: $package_dir/${image_name}_docker.img"
    elif [ "x$1" == "x6" ]
    then
        ./docker_img.sh -f Dockerfile.du_dpdk -t $docker_image -n $image_name || exit 1
        chmod a+r ${image_name}_docker.img
        mv -b -f ${image_name}_docker.img $package_dir || exit 1
        echo "Image available at: $package_dir/${image_name}_docker.img"
    elif [ "x$1" == "x7" ]
    then
        ./docker_img.sh -f Dockerfile.dsim -t $docker_image -n dsim || exit 1
        chmod a+r dsim_docker.img
        mv -b -f dsim_docker.img $package_dir || exit 1
    elif [ "x$1" == "x8" ]
    then
        ./docker_img.sh -f Dockerfile.mmwrnsim_dpdk -t $docker_image -n $image_name || exit 1
        chmod a+r ${image_name}_docker.img
        mv -b -f ${image_name}_docker.img $package_dir
        echo "Image available at: $package_dir/${image_name}_docker.img"
    fi
}

function stop_docker() {
    cont_name=`get_container_id $1`
    if [ ! -z "$cont_name" ]
    then
        echo "Stopping the docker container id:[$cont_name]"
        docker stop $cont_name
    else
        echo "No Container exists"
        exit 1
    fi
}

function assign_interface_to_container() {
    container_name=$1
    vf=$2
    pid=`docker inspect -f '{{.State.Pid}}' $container_name`
    ln -s /proc/$pid/ns/net /var/run/netns/$pid
    ip link set $vf netns $pid
}

function interface_to_container()
{
# Used to provide IP address to mmwSIM & DUSIM using virtual function.
    interface_name=$1
    container_name=$2
    # Add dummy NS to create /var/run/netns dir
    ip netns add abc

    # Wait for container to start.
    running=`docker ps -q -f name=$container_name | wc -l`
    while [ $running -lt 1 ]
    do
        echo "Wating for container to start: Container Name: $container_name"
        running=`docker ps -q -f name=$container_name | wc -l`
        sleep 5
    done

    # Get Container Process ID
    container_process_id=`docker inspect -f '{{.State.Pid}}' $container_name`
    echo "Container Process ID is: $container_process_id"

    # Assign interface to container network Name space
    echo "Assigning interface($interface_name) to container($container_name)"
    sleep 3
    ln -s /proc/$container_process_id/ns/net /var/run/netns/$container_process_id
    ip link set $interface_name netns $container_process_id

    sleep 3
    ip netns exec $container_process_id ip link set $interface_name up
}

function start_docker_image() {
    cont_name=$(get_container_id $1)
    docker_image=$(get_docker_image_name $1)
    # Use cu_dpdk pkg for mode=3 (cu non-fe mode)
    if [[ "$1" -eq 3 ]]
    then
        docker_image=$(echo ${nrdockerimage}_cu_dpdk:$nrdockerversion)
    fi
    host_port=$(get_host_port_log $1)
    host_port_gdb=$(get_host_port_gdb)
    mount_cmd=""
    if [ ! -z "$MOUNT_PATH" ]
    then
        mount_cmd="-v $MOUNT_PATH:$MOUNT_PATH"
        echo "mount_cmd :: $mount_cmd"
    fi
    if [ -z "$cont_name" ]
    then
        echo "No docker image running. Starting one"
        cont_name=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32`
        cont_name=${XU_NAME}
        #Docker image
        #   - name is given (--name)
        #   - host port mapping (-p) host-machine-port:container-port
        #   - --security-opt seccomp=unconfined - to make gdb breakpoint to work
        #   - --privileged - so that process can overwrite value /proc/sys/vm/drop_caches
        #   - --cap-add=sys_nice --cpu-rt-runtime=950000 :: so that sched_setscheduler() call succeeds
        #For running telnet
        #docker run --rm --name $cont_name -v /sys/fs/cgroup:/sys/fs/cgroup:ro --privileged --cap-add=sys_nice --cpu-rt-runtime=50000 --security-opt seccomp=unconfined -p$host_port:50003 $docker_image &
        #docker run --rm --net testnw --ip=10.12.111.229 --name $cont_name $mount_cmd  --privileged --cap-add=sys_nice --cpu-rt-runtime=50000 --security-opt seccomp=unconfined -p$host_port_gdb:$container_port_gdb_server -p$host_port:50003 $docker_image &
        #docker run --rm --name $cont_name $mount_cmd  --privileged --cap-add=sys_nice --cpu-rt-runtime=50000 --security-opt seccomp=unconfined -p$host_port_gdb:$container_port_gdb_server -p$host_port:50003 $docker_image &
        #docker run --rm --name $cont_name  --privileged --cap-add=sys_nice --cpu-rt-runtime=50000 --security-opt seccomp=unconfined  -p$host_port:50003 $docker_image &

        #for DPDK docker run command is different
        if [ "x$1" == "x4" ] || [ "x$1" == "x9" ]
        then
            docker run -it --name $cont_name $mount_cmd --privileged --cap-add=ALL --security-opt seccomp=unconfined -v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
                -v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
                -v /sys/devices/system/node:/sys/devices/system/node \
                -v /dev:/dev \
                -v /lib/modules:/lib/modules \
                -d \
                -e MODE=$1 \
                -v $SCW_DB_VOL:/enc_data \
                -v $SCW_DATA_VOL:/scw/lvm_mounts \
                -e PCI_DEVICE_LIST_DOCKER="${XU_NIC_LIST}" \
                -e FE_NUM_CORES="1" \
                -e NUM_HUGEPAGES="40" \
                -e SCOS_CLEAN_DATA="1" \
                 $docker_image
        elif [ "x$1" == "x5" ]  # DUSIM
        then
            source `pwd`/env.sh
            docker run --name $cont_name $mount_cmd --privileged --cap-add=ALL --security-opt seccomp=unconfined \
                -v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
                -v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
                -v /sys/devices/system/node:/sys/devices/system/node \
                -v /dev:/dev -v /lib/modules:/lib/modules \
                -e interface_name=$interface_name -e cu_name=$cu_name -e cu_ip=$cu_ip -e MODE=$1 \
                -e PCIDEVICE_INTEL_COM_INTEL_FEC_5G=6a:00.1 \
                -e PCIDEVICE_INTEL_COM_INTEL_SRIOV_DPDK="0000:b3:0a.0 0000:b3:0a.1" $docker_image &

            interface_to_container $interface_name $cont_name
        elif [ "x$1" == "x6" ]  # DU
        then
            docker run -it --name $cont_name $mount_cmd --privileged --cap-add=ALL --security-opt seccomp=unconfined \
                -v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
                -v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
                -v /sys/devices/system/node:/sys/devices/system/node \
                -v /dev:/dev -v /lib/modules:/lib/modules \
                -d \
                -e MODE=$1 \
                -e PCIDEVICE_INTEL_COM_INTEL_FEC_5G=6a:00.1 \
                -e PCIDEVICE_INTEL_COM_INTEL_SRIOV_DPDK="0000:b3:0a.0 0000:b3:0a.1"
                -e PCI_DEVICE_LIST_DOCKER="${XU_NIC_LIST}" \
                $docker_image
        elif [ "x$1" == "x8" ]   # mmwSIM
        then
            source `pwd`/env.sh
            docker run --name $cont_name $mount_cmd --privileged --cap-add=ALL --security-opt seccomp=unconfined -v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
                -v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
                -v /sys/kernel/mm/hugepages/hugepages-2048kB:/sys/kernel/mm/hugepages/hugepages-2048kB \
                -v /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages:/sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages \
                -v /sys/devices/system/node:/sys/devices/system/node \
                -v /dev:/dev \
                -v /lib/modules:/lib/modules -e interface_name=$interface_name -e cu_name=$cu_name -e cu_ip=$cu_ip -e MODE=$1 $docker_image &

            interface_to_container $interface_name $cont_name
        else
            #echo "Running docker command ::: docker run --rm --name $cont_name $mount_cmd  --privileged --cap-add=sys_nice --cpu-rt-runtime=50000 --security-opt seccomp=unconfined -p$host_port_gdb:$container_port_gdb_server -p$host_port:50003 $docker_image &"
            docker run -it --name $cont_name $mount_cmd --privileged --cap-add=sys_nice --security-opt seccomp=unconfined -v /dev:/dev -e MODE=$1 $docker_image
        fi
    else
	# For DataSim, ultiple containers may be run so we don't want to force user to stop
        if [ "x$1" == "x7" ]
        then
	    vf=$DS_SELF_VF
	    ds_ip=$DS_SELF_IP
	    cu_ip=$DS_CU_IP
	    cu_to_du_cpu=$DS_CU_DU_CPU
	    cu_to_cn_cpu=$DS_CU_CN_CPU
	    du_to_cu_cpu=$DS_DU_CU_CPU
	    cn_to_cu_cpu=$DS_CN_CU_CPU
            cont_name_num=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 10`
	    cont_name=DS_0_${cont_name_num}
	    echo "Starting DataSim container ${cont_name} with ${docker_image} connecting to device ${vf} with address ${ds_ip} and CU address ${cu_ip}"
            docker run -t -d  --name $cont_name  --privileged --cap-add=ALL --security-opt seccomp=unconfined \
		-e MODE=7 \
		-e DS_SELF_VF=$vf -e DS_SELF_IP=$ds_ip -e DS_CU_IP=$cu_ip \
		-e DS_CU_DU_CPU=$cu_to_du_cpu -e DS_CU_CN_CPU=$cu_to_cn_cpu -e DS_DU_CU_CPU=$du_to_cu_cpu -e DS_CN_CU_CPU=$cn_to_cu_cpu \
		$docker_image
	    assign_interface_to_container $cont_name $vf
	else
            echo "Docker image running. Id :[$cont_name]. Please stop it before running other instance..."
	fi
    fi
}

function validate_ws_root() {
    if [ ! -d $1 ]; then
        echo "Workspace root directory doesn't exist.Please check "
        echo "that you have completed building the entire workspace"
	    usage
        exit 1
    fi
    base_name=`basename $1`
    if [[ $base_name =~ pkg.* ]]; then
	echo hmm: not using the default pkg.developer
	ws_root=`dirname $1`
	pkg_dir=$base_name
    else
	ws_root=$1
	pkg_dir=pkg.developer
    fi

    echo "Valid workspace root: $ws_root"
    if [ -d $ws_root/lte_fns ] && [ -d $ws_root/platform ] && [ -d $ws_root/uber ] && [ -d $ws_root/5g_fns ] && [ -d $ws_root/${pkg_dir} ] && [ -d $ws_root/hardware ] ;
    then
        if [ "x$2" == "x5" ] || [ "x$2" == "x6" ]; then
                package_file=$ws_root/${pkg_dir}/x86_DU_release/x86_DU_*[0-9]
        elif [ "x$2" == "x8" ]; then
                package_file=$ws_root/${pkg_dir}/x86_MMWRNSIM_release/x86_MMWRNSIM_*[0-9]
        elif [ "x$2" == "x9" ]; then
	        package_file=$ws_root/${pkg_dir}/x86_CU_appliance_release/x86_CU_*[0-9]
        else
	        package_file=$ws_root/${pkg_dir}/x86_CU_release/x86_CU_*[0-9]
        fi
    	package_dir=`dirname $package_file`
	    if [ ! -r  $package_file ]; then
	        echo "can't read package file $package_file"
	        echo "check that the workspace build has completed"
	        exit 1
    	fi

        echo "Package file: $package_file"
	    image_name=`basename $package_file`
    else
        echo ""
        echo ""
        echo "Incorrect workspace root directory.Please check "
        echo "that you have completed building the entire workspace"
	    usage
        exit 1
    fi
}

function validate_prepare_build() {
    validate_ws_root $1 $SETUP
    prepare_tar $ws_root $SETUP
    build_docker_image $SETUP
}

MOUNT_PATH=""
function main() {
    SETUP=4
    scriptpath="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
    workspace="$(dirname $(dirname $(dirname $scriptpath)))"
    destination="$workspace"

    echo "Script path: $scriptpath"
    cd $scriptpath

    if [ "$#" -lt 1 ];
    then
        # If no params are provided, we will assume this is a request for a dev build in the current workspace (same as the default for the SCONS command)
        echo "No params provided: building developer docker image: $destination"
        validate_prepare_build $destination
        exit
    elif [[ $@ = *" -b"* ]] && [[ $@ = *" --buildtype"* ]]; then
        echo ""
        echo "Cannot use the -b option with --buildtype.  If using --buildtype, your workspace path will be determined automatically."
        echo ""
        usage
        exit 1
    fi

    while [ "$1" != "" ];
    do
        case $1 in
            -h | --help )
                usage
                exit
                ;;
            -b | --build_docker_image)
                shift
                if [ "x$1" == "x" ] || [[ "$1" = -* ]]
                then
                    # No workspace path provided - determine based on location of this script (dev build)
                    validate_prepare_build $destination
                elif [ -d $1 ]
                then
                    validate_prepare_build $1
                else
                    echo "Workspace root [$1] not exists... Check -h..Exiting"
                    exit 1
                fi
                ;;
            -e | --build_docker_image_existing_tar)
                echo "Building docker image for $SETUP"
                build_docker_image $SETUP
                ;;
            -i | --interactive_shell)
                interactive_shell $SETUP
                ;;
            -g | --gdb_server_start)
                if [ -z "$2" ]
                then
                    echo "Wrong number of arguments. Process name not provided.. Exiting.."
                    exit
                fi
                gdb_server_start $SETUP $2
                shift
                ;;
            -l | --log)
                host_port=`get_host_port_log $SETUP`
                echo "Host port for SETUP:$SETUP is $host_port"
                #python ./telnet_reader.py ${hostportfordebug} | egrep -v '^[ ]*$'
                python ./telnet_reader.py ${host_port}
                ;;
            -m | --mount_workspace)
                if [ -z "$2" ]
                then
                    echo "Wrong number of arguments. Workspace space path not provided.. Exiting.."
                    exit
                fi
                if [ ! -d $2 ]
                then
                    echo "Worspace path not accessible or not existing... Exiting.."
                    exit 1
                else
                    MOUNT_PATH=$2
                    shift
                    echo "MOUNT_PATH set to :: $MOUNT_PATH"
                fi
                ;;
            -r | --run_docker)
                start_docker_image $SETUP
                ;;
            -s | --stop)
                stop_docker $SETUP
                ;;
            -p | --prepare_tar)
                shift
                validate_ws_root $1
                prepare_tar $1 $SETUP
                ;;
            -u | --update_process)
                shift
                if [ -f $1 ]
                then
                    echo "Updating $1 in docker image for $SETUP"
                    update_process $SETUP $1
                else
                    echo "File path[$2] not exists... Check -h..Exiting"
                    exit 1
                fi
                ;;
            -c | --cleanup)
                cleanup
                ;;
            -t | --type)
                shift
                if [ "x$1" == "x4" ] || [ "x$1" == "x9" ]; then
                    SETUP=$1
                elif [ "x$1" == "x5" ] || [ "x$1" == "x6" ] || [ "x$1" == "x7" ] || [ "x$1" == "x8" ]; then
                    SETUP=$1
                else
		        #if [ "x$1" == "x1" ] || [ "x$1" == "x2" ]  || [ "x$1" == "x3" ]  [ "x$1" == "x5" ] || [ "x$1" == "x6" ]                then
                    echo "Wrong build type:[$1] ... Check -h..Exiting"
        		    usage
                    exit 1
                fi
                ;;
            --buildtype=test | --buildtype=release | --buildtype=developer | --buildtype)
                # Get the path of this script so we can determine the workspace root automatically
                workspace="$(dirname $(dirname $(dirname $scriptpath)))"
                destination="undefined"

                if [ "x$1" == "x--buildtype=test" ]; then
                    destination=$workspace"/pkg.test"
                elif [ "x$1" == "x--buildtype=release" ]; then
                    destination=$workspace"/pkg.release"
                elif [ "x$1" == "x--buildtype=developer" ]; then
                    destination=$workspace"/pkg.developer"
                elif [ "x$1" == "x--buildtype" ]; then
                    shift
                    if [ "x$1" != "xtest" ] && [ "x$1" != "xrelease" ] && [ "x$1" != "xdeveloper" ]; then
                        echo "'$1' is not a valid --buildtype option, must be 'test', 'release', or 'developer', exiting..."
                        exit 1
                    fi
                    destination=$workspace"/pkg.$1"
                fi
                shift

                if [ -d $destination ]
                then
                    validate_prepare_build $destination
                else
                    echo "Workspace root [$destination] doest not exist, exiting..."
                    exit 1
                fi
                ;;
            *)
                echo "Invalid argument::$1"
                usage
                exit 1
        esac
        shift
    done
    return 0
}
precheck
main $*
exit $?
