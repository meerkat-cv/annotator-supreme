#!/bin/bash
if ! git diff-index --quiet HEAD --
then 
    echo "ERROR: You have uncommitted changes, commit or stash them before building the Dockerfile."
    exit 1
fi

sudo docker build -t annotator_supreme --build-arg SOURCE_COMMIT=$(git rev-parse HEAD) -f Dockerfile .
