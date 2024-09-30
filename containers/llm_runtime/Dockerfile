FROM nvidia/cuda:12.2.2-devel-ubuntu22.04


RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        git \
        locales \
        sudo \
        build-essential \
        dpkg-dev \
        wget \
        openssh-server \
        nano \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*


RUN CUDACXX=/usr/local/cuda-12/bin/nvcc CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=all-major" FORCE_CMAKE=1 \
    pip install "llama-cpp-python[server]" --no-cache-dir --force-reinstall --upgrade

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

