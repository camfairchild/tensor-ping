#!/bin/bash
app="tensor-ping"
docker kill ${app}
docker container rm ${app}
bash start.sh