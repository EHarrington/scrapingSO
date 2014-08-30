#!/bin/bash
SOURCE=$1
DEST=$2

sed 's/\ /./g' $SOURCE > temp.tmp
sed 's/,/\ /g' temp.tmp > $DEST
rm temp.tmp