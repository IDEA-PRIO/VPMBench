#!/usr/bin/env bash

cd /CADD-scripts
./CADD.sh -g GRCh37 -o cadd-output.tsv.gz $1
gunzip cadd-output.tsv.gz 

tail -n +2 cadd-output.tsv | awk -F '\t' 'NR==1{print "CHROM,POS,REF,ALT,SCORE"} NR>1{printf("%s,%s,%s,%s,%s\n",$1,$2,$3,$4,$NF)}' > $2

