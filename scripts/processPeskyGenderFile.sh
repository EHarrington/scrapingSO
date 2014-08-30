#!/bin/bash
sed 's/\ /./g' StackoverflowGenderInformation1.csv > StackGenderInfo1.tmp
sed 's/,/\ /g' StackGenderInfo1.tmp > StackGenderInfo1.txt
tr -d '\015' <StackGenderInfo1.txt >StackGenderInfo1.tmp
sed 's/\/users/\
\/users/g' StackGenderInfo1.tmp > StackGenderInfo1.txt 

rm StackGenderInfo1.tmp