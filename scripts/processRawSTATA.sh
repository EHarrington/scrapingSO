#!/bin/bash
YEAR=$1
SOURCE=Stack$YEAR.raw
DEST=Stack$YEAR.txt
TEMP=Stack$YEAR.tmp

tr -s '[:blank:]' ',' < $SOURCE > $DEST
tr -d '"' < $DEST > $TEMP
tr "\n\r" "," < $TEMP > $DEST
tr -s  "," < $DEST > $TEMP
sed 's/,'$YEAR',/\
/g' $TEMP > $DEST
rm $TEMP