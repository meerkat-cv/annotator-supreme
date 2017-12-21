#!/bin/bash

sudo docker ps | grep cassandraDB
if [ $? -ne 0 ]
then 
    echo "Init Cassandra database"
    ./initCassandra.sh
fi

sudo docker ps -a | grep annotator_dev
if [ $? -ne 0 ]
then 
    CLUSTER_IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' cassandraDB)
    echo "Using cassandra database from:" $CLUSTER_IP
    echo "Running new container annotator_dev ..."

    sudo docker run -itd -P \
	-v $(pwd):/code \
	--env CLUSTER_IP=$CLUSTER_IP \
	--hostname annotator.dev.intranet \
	--name annotator_dev \
	--add-host=cassandraDB:$CLUSTER_IP annotator_supreme
else
    sudo docker start annotator_dev
    echo -n "Starting annotator_dev container ..."
fi

status=1
while [ $status -ne 0 ]; 
do 
    out=$(sudo docker logs -f --since='10s' annotator_dev | grep -m1 'INFO:annotator_supreme:App built successfully!')
    status=$?; 
    echo -n "."
    sleep 1s
done; 
echo "DONE"
echo $out

IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' annotator_dev)
echo "container annotator_dev running at http://$IP/annotator-supreme/"
sudo docker port annotator_dev
