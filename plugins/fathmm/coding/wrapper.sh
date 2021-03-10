#!/usr/bin/env bash

python2 /fathmm-MKL/fathmm-MKL.py $1 /fathmm-result.tsv /fathmm-MKL/fathmm-MKL_Current.tab.gz
cat /fathmm-result.tsv | awk -F '\t' 'NR==1{print "CHROM,POS,REF,ALT,SCORE"} NR>1{printf("%s,%s,%s,%s,%s\n",$1,$2,$3,$4,$7)}' > $2