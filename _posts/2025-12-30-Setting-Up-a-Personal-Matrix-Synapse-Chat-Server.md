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

Communication will travel through the path outlined below. We will use the Element app (client) to send messages through a Cloudflare tunnel to our Apache reverse proxy, which will route it to our Synapse server. 

<img src="/img/matrix/matrix1.png" height="100%" width="100%" class="inline"/>
# Installation
We will follow the installation process in reverse, starting with out Matrix Synapse server. 

## Synapse
There are a few ways to install a Matrix Synapse server, but a fairly straightforward way is to do it via a docker image found here: [synapse](https://hub.docker.com/r/matrixdotorg/synapse)

Pull the Docker image and set up the initial config by running the below: 

  `docker run -it --rm \`
      `--mount type=volume,src=synapse-data,dst=/data \`
      `-e SYNAPSE_SERVER_NAME=my.matrix.host \`
      `-e SYNAPSE_REPORT_STATS=yes \`
      `matrixdotorg/synapse:latest generate`

*substitue my.matrix.host for your personal domain name.* 

There will now be a Docker volume which includes the config file `homeserver.yaml` that will control how Synapse behaves. 

The first change we will make is to the database spporting Synapse. Initially, it ships with SQLite but we will install PostgreSQL and edit out yaml file for the change. 

Install and connect to PostgreSQL to setup a user and db for Synapse: 

  `sudo su -l postgres`
  `createuser --pwprompt synapse_user`
  `createdb --encoding=UTF8 --locale=C --template=template0 --owner=synapse_user synapse`

Once that's complete we can edit the `homeserver.yaml` file to link the new db 

  `database:`
    `name: psycopg2`
    `args:`
      `user: synapse_user`
      `password: [the password you created]`
      `database: synapse`
      `host: 127.0.0.1`
      `cp_min: 1`
      `cp_max: 25`









