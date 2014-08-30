#!/bin/bash

sed 's/\ /./g' StackoverflowGenderInformation$1.csv > StackGenderInfo$1.tmp
sed 's/,/\ /g' StackGenderInfo$1.tmp > StackGenderInfo$1.txt
rm StackGenderInfo$1.tmp