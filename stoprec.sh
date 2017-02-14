#!/bin/bash
TIMESTAMP=`cat /home/liquidsoap/stamp$3`
(
sleep 2 
echo 'dynamic_file.stop '$1$TIMESTAMP'_'$2
sleep 2
echo "exit"
) | socat /home/liquidsoap/socket -
