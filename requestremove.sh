#!/bin/bash
( echo request_$1.remove $2
echo exit ) | socat /home/liquidsoap/socket -
