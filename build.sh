#!/bin/bash
docker build -t so2harbor.com:6000/library/crawlerapp:latest --network=host .
docker push  so2harbor.com:6000/library/crawlerapp:latest
