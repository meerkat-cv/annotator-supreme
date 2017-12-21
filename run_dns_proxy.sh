#!/bin/bash
sudo docker run --hostname dns.mageddo --name dns-proxy-server -p 5380:5380 \
    -v /opt/dns-proxy-server/conf:/app/conf \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /etc/resolv.conf:/etc/resolv.conf \
    defreitas/dns-proxy-server
