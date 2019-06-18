#!/bin/bash
# helper script for NeighborNet creation
# usage: make_neighbornets.sh PATH_TO_SPLITSTREE_COMMAND
BASE_PATH=`realpath .`
SPLITSTREE_CMD=`realpath $1`
for i in analyses/*
do
    cd $i
    echo "Processing $i"
    $SPLITSTREE_CMD -g -c $BASE_PATH/splitstree_cmds.txt
    cd $BASE_PATH
done



