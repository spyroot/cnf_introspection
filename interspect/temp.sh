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