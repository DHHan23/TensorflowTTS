FROM tensorflow/tensorflow:2.3.1-gpu
ENV NVIDIA_VISIBLE_DEVICES all

RUN apt-get update && apt-get install -y \
    build-essential \
    zsh \
    tmux \
    curl \
    wget \
    unzip \
    git \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir ipython jupyter gdown tensorboard

RUN mkdir /content
ADD . /content/TensorflowTTS
WORKDIR /content/TensorflowTTS

RUN pip install --no-cache-dir .

EXPOSE 8888
EXPOSE 6006

CMD ["/bin/bash"]
