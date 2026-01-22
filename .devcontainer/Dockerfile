FROM osrf/ros:humble-desktop-full

RUN apt-get update && apt-get install -y \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1 \
    mesa-utils \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*