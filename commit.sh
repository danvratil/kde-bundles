#!/bin/sh

name="$1"

if [ -z "$COMMITMSG" ]; then
    echo "$1: build" > build/${name}/.COMMITMSG
    nano build/${name}/.COMMITMSG
else
    echo "$1: $COMMITMSG" > build/${name}/.COMMITMSG
fi

