#!/bin/bash
CLUSTER_IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' cassandraDB)
echo $CLUSTER_IP

sudo docker rm annotator_supreme_dev
sudo docker run -itd -P \
       -v $(pwd):/home \
       --env CLUSTER_IP=$CLUSTER_IP \
       --hostname annotator.dev.intranet \
       --name annotator_supreme_dev \
       --add-host=cassandraDB:$CLUSTER_IP annotator_supreme bash

sudo docker exec annotator_supreme_dev bash -c "/usr/local/nginx/sbin/nginx & cd /home ; python3 run_api.py"
