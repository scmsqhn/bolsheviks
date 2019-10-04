#!/bin/bash
echo from $1
echo to $2
more $1 |awk -F ',' '{print $3","$4}' | sort | uniq > $2
wc -l $1
wc -l $2
