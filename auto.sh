#!/bin/bash

while true
do
  git add .
  git commit -m "auto update $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
  git push origin main
  sleep 60
done

