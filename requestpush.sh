#!/bin/bash
( echo request_$1.push $2
echo exit ) | socat /home/liquidsoap/socket - > /home/liquidsoap/request_$1.log
