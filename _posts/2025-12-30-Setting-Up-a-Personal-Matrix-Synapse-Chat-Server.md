---
layout: default
title: Personal Matrix Chat Server With Synapse
---

# Personal Matrix Chat Server With Synapse

During the holidays I embarked on a journey to set up a matrix synapse server on my old MacBook Air running linux mint cinnamon. 

Matrix synapse is a decentralized federated communications system that can be self-hosted on your home server.

I chronicled my journey here to help future adventurers: 

### You will need to sign up/already have a few services for this project: 

1. Valid e-mail.
2. Personal domain name. 
3. Cloudflare free tier account.

## Architecture

Communication will travel through the path outlined below. We will use Element (client) to send our communications through a clooudflare tunnel to our apache reverse proxy, which will route it to our Synapse server. 

<img src="/img/matrix/matrix1.png" height="100%" width="100%" class="inline"/>

# Installation
We will follow the installation process in reverse, starting with out Matrix Synapse server. 

## Synapse
There are a few ways to install a matrix synapse server, but a fairly straightforward way is to do it via a docker image found here: [synapse](https://hub.docker.com/r/matrixdotorg/synapse)

Pull the docker image and set up the initial config by running the below: 

  `docker run -it --rm \
      --mount type=volume,src=synapse-data,dst=/data \
      -e SYNAPSE_SERVER_NAME=my.matrix.host \
      -e SYNAPSE_REPORT_STATS=yes \
      matrixdotorg/synapse:latest generate`

*substitue my.matrix.host for your personal domain name.* 





