#!/bin/bash
CLUSTER_IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' cassandraDB)
echo $CLUSTER_IP

sudo docker rm annotator_supreme
sudo docker run -d -P \
     --env CLUSTER_IP=$CLUSTER_IP \
     --hostname annotator.prod.intranet \
     --name annotator_supreme \
     --add-host=cassandraDB:$CLUSTER_IP annotator_supreme
