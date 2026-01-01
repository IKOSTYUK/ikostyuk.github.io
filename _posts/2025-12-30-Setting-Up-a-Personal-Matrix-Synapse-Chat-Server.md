---
layout: default
title: Personal Matrix Chat Server With Synapse
---

# Personal Matrix Chat Server With Synapse

During the holidays I embarked on a journey to set up a Matrix Synapse server on my old MacBook Air running Linux Mint Cinnamon. Matrix is a decentralized federated communications system that can be self-hosted on your home server. I chronicled my journey here to help future adventurers: 

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
There are a few ways to install a Matrix Synapse server, but a fairly straightforward way is to do it via a docker image found here: [Synapse Docker Image](https://hub.docker.com/r/matrixdotorg/synapse)

Pull the Docker image and set up the initial config by running the below: 

    docker run -it --rm \
      --mount type=volume,src=synapse-data,dst=/data \ 
      -e SYNAPSE_SERVER_NAME=my.matrix.host \
      -e SYNAPSE_REPORT_STATS=yes \
      matrixdotorg/synapse:latest generate

*substitue my.matrix.host for your personal domain name.* 

There will now be a Docker volume which includes the config file `homeserver.yaml` that will control how Synapse behaves. 

The first change we will make is to the database spporting Synapse. Initially, it ships with SQLite but we will install PostgreSQL and edit out yaml file for the change. Install and connect to PostgreSQL to setup a user and db for Synapse: 

      sudo su -l postgres
      createuser --pwprompt synapse_user
      createdb --encoding=UTF8 --locale=C --template=template0 --owner=synapse_user synapse

Once that's complete we can edit the `homeserver.yaml` file to link the new db: 

      database:
        name: psycopg2
        args:
          user: synapse_user
          password: [the password you created]
          database: synapse
          host: 127.0.0.1
          cp_min: 1
          cp_max: 25

## Apache

Setting up an Apache reverse proxy will help with security and routing. Apache will run on port 443 and hand off traffic to Synapse on port 8008. We will configure all of Matrix communication to run on port 443 regardless of server-server or client-server traffic. That will help us simplify the process, especially with the Cloudflare tunnel, which will connect directly to 443. 

Will Lewis gives an example of the VirtualHost file implementation on [his blog](https://willlewis.co.uk/blog/posts/run-your-own-matrix-server-guide/) which we can add as .conf file in our Apache2 sites-enabled directory:

    <VirtualHost *:443>
            ServerName example.com
            AllowEncodedSlashes NoDecode
            ServerAdmin email@example.com
            ServerAlias example.com www.example.com
            DocumentRoot /var/www/html/example.com
    
            <Location /_matrix>
                    RequestHeader set "X-Forwarded-Proto" expr=%{REQUEST_SCHEME}
                    ProxyPreserveHost On
                    ProxyPass "http://127.0.0.1:8008/_matrix" nocanon
                    ProxyPassReverse "http://127.0.0.1:8008/_matrix"
            </Location>
    
            <Location /_synapse/client>
                    RequestHeader set "X-Forwarded-Proto" expr=%{REQUEST_SCHEME}
                    ProxyPreserveHost On
                    ProxyPass "http://127.0.0.1:8008/_synapse/client" nocanon
                    ProxyPassReverse "http://127.0.0.1:8008/_synapse/client"
            </Location>
    
            # Logging options
            # SSL Options
    </VirtualHost>

*substitue the first few server rows for your personal domain name.*








