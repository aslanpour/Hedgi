#!/bin/bash
for ip in $(seq 1 1 7)
do
  echo "copy hedgi.py and utils.py to ~ at 10.0.0.9$ip"
  scp ~/hedgi.py ubuntu@10.0.0.9$ip:.
  scp ~/utils.py ubuntu@10.0.0.9$ip:.

done
