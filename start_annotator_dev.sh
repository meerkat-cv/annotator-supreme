#!/bin/bash
sudo docker start annotator_dev

echo "Initializing annotator_dev ..."

sudo docker logs -f --since="10s" annotator_dev | grep -m1 "INFO:annotator_supreme:App built successfully!" && \
    IP=$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' annotator_dev)

echo "Annotator running: http://$IP/annotator-supreme/"
