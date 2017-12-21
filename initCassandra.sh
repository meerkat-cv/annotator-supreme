#!/bin/bash
sudo docker ps -a | grep cassandraDB
if [ $? -ne 0 ]
then
    echo "Running new container cassandraDB ..."
    out=$(sudo docker run -d --name cassandraDB cassandra:latest)
else
    sudo docker start cassandraDB
    echo -n "Starting cassandraDB container ..."
    status=1; 
    while [ $status -ne 0 ]; 
    do 
	out=$(sudo docker exec cassandraDB cqlsh -e "SHOW HOST" 2>1 ); 
	status=$?; 
	echo -n "."
    done; 
fi 

echo "DONE"
echo $out

