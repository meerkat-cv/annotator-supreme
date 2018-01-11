#!/bin/bash
if ! git diff-index --quiet HEAD --
then 
    echo "ERROR: You have uncommitted changes, commit or stash them before building the Dockerfile."
    exit 1
fi

#sudo SOURCE_COMMIT=$(git rev-parse HEAD)
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --build-arg SOURCE_COMMIT=$(git rev-parse HEAD) annotator

