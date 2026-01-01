---
layout: default
title: Personal Matrix Chat Server With Synapse
---

# Personal Matrix Chat Server With Synapse

During the holidays, I embarked on a journey to set up a Matrix Synapse server on my old MacBook Air running Linux Mint Cinnamon. Matrix is a decentralized federated communications system that can be self-hosted on your home server. I chronicled my journey here to help future adventurers: 

### You will need to sign up/already have a few services for this project: 

1. Valid e-mail.
2. Personal domain name. 
3. Cloudflare free tier account.

## Architecture

Communication will travel through the path outlined below. We will use the Element app (client) to send messages through a Cloudflare tunnel to our Apache reverse proxy, which will route it to our Synapse server. 

<img src="/img/matrix/matrix1.png" height="100%" width="100%" class="inline"/>
# Installation
We will follow the installation process in reverse, starting with our Matrix Synapse server. 

## Synapse
There are a few ways to install a Matrix Synapse server, but a fairly straightforward way is to do it via a Docker image found here: [Synapse Docker Image](https://hub.docker.com/r/matrixdotorg/synapse)

Pull the Docker image and set up the initial config by running the below: 

    docker run -it --rm \
      --mount type=volume,src=synapse-data,dst=/data \ 
      -e SYNAPSE_SERVER_NAME=my.matrix.host \
      -e SYNAPSE_REPORT_STATS=yes \
      matrixdotorg/synapse:latest generate

*Substitute my.matrix.host for your personal domain name.* 

There will now be a Docker volume which includes the config file `homeserver.yaml` that will control how Synapse behaves. 

The first change we will make is to the database spporting Synapse. Initially, it ships with SQLite but we will install PostgreSQL and edit out `homeserver.yaml` file for the change. Install and connect to PostgreSQL to setup a user and db for Synapse: 

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

Additional documentation for the config file can be found here: [Synapse Installation Guide](https://matrix-org.github.io/synapse/latest/usage/configuration/config_documentation.html)


## Apache

Setting up an Apache reverse proxy will help with security and routing. Apache will run on port 443 and hand off traffic to Synapse on port 8008. We will configure all of Matrix communication to run on port 443 regardless of server-server or client-server traffic. That will help us simplify the process, especially with the Cloudflare tunnel, which will connect directly to 443. 

Will Lewis gives an example of the VirtualHost file implementation on [his blog](https://willlewis.co.uk/blog/posts/run-your-own-matrix-server-guide/), which we can add as .conf file in our Apache2 sites-enabled directory:

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

*Substitute the first few server rows for your personal domain name.*

Once that's complete we should also set up our SSL certificates for Apache to utilize. Assuming we still have no access to the outside world via our network, we can do this with the Let's Encrypt DNS-01 Challenge and verify the TXT record manually. 

## Cloudflare

Instead of port fowarding with our router, we will instead use a Cloudflare tunnel for a more secure connection. Install cloudflare tunnel via Docker and make sure it points inside the docker container https://host.docker.internal:443 so it can communicate with Apache locally. 

Finally, we need to configure the .well-known files in either Apache or Cloudflare. These files help other clients and servers to be able to locate and dsicvoer your Matrix server through the tunnel. To reduce the load on the Apache server, we will intercept these requests with Cloudflare by using a Cloudflare worker:

    const HOMESERVER_URL = "https://matrix.yourdomain.com"; // Your Synapse URL
    const SERVER_NAME = "matrix.yourdomain.com:443";      // Your federation address
    
    export default {
      async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname;
    
        // Define the JSON responses
        const clientConfig = {
          "m.homeserver": { "base_url": HOMESERVER_URL }
        };
        
        const serverConfig = {
          "m.server": SERVER_NAME
        };
    
        // Routing logic
        if (path === "/.well-known/matrix/client") {
          return new Response(JSON.stringify(clientConfig), {
            headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
          });
        }
    
        if (path === "/.well-known/matrix/server") {
          return new Response(JSON.stringify(serverConfig), {
            headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
          });
        }
    
        // Pass everything else through to your Apache proxy/Origin
        return fetch(request);
      }
    };

We also want to configure worker routes to trigger only for the specific Matrix discovery paths. Add the following two routes (replace yourdomain.com with your apex domain):

    yourdomain.com/.well-known/matrix/client

    yourdomain.com/.well-known/matrix/server

# Running Synapse

We are finally ready to run Synapse with the following command: 

    docker run -d --name synapse \
        --mount type=volume,src=synapse-data,dst=/data \
        -p 8008:8008 \
        matrixdotorg/synapse:latest

*Make sure to change -p 8008:8008 to  -p 127.0.0.1:8008:8008 so Synapse listens only to your local Apache server and is not exposed publically.*

If all goes well and you visit http://localhost:8008 you should see:
<img src="/img/matrix/matrix2.png" height="100%" width="100%" class="inline"/>

You can also use the [Matrix Federation Tester](https://federationtester.matrix.org/) for additional checks. 

Fire up your Element app and login!
<img src="/img/matrix/matrix3.PNG" height="100%" width="100%" class="inline"/>







