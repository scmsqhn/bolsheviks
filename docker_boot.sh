#!/bin/bash
nvidia-docker run \
  -v $PWD:/home/ultrastar/bolshevik \
  -P \
  --name bolshevik \
  -itd tensor:latest /bin/bash

#nvidia-docker run -v /home/siy/bert:/home/siy/bert --name bert -itd tensorflow/tensorflow:1.12.0-gpu-py3 
