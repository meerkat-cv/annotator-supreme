#!/bin/bash
CLUSTER_IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' cassandraDB)
echo "Using cassandra database from:" $CLUSTER_IP

echo "Initializing annotator_supreme ..."
sudo docker run -d -P \
     --env CLUSTER_IP=$CLUSTER_IP \
     --hostname annotator.prod.intranet \
     --name annotator_supreme \
     --add-host=cassandraDB:$CLUSTER_IP annotator_supreme

sudo docker logs -f --since="10s" annotator_supreme | grep -m1 "INFO:annotator_supreme:App built successfully!" && \
IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' annotator_supreme)

echo "Annotator running: http://$IP/annotator-supreme/"
