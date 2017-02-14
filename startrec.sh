#!/bin/bash
TIMESTAMP=`date +%Y-%m-%d_%H-%M-%S`
> stamp$3
echo $TIMESTAMP > /home/liquidsoap/stamp$3
(
sleep 2 
echo 'dynamic_file.start '$1$TIMESTAMP'_'$2
sleep 2
echo "exit"
) | socat /home/liquidsoap/socket -
