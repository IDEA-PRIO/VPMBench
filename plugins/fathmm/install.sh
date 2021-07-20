#!/usr/bin/env bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

echo "INSTALLING fathmm-MKL"
echo "====================="
echo ""

echo "> Download Files (Approx. 80GB)"
wget http://fathmm.biocompute.org.uk/database/fathmm-MKL_Current.tab.gz

echo "> Build index"
tabix -f -p bed fathmm-MKL_Current.tab.gz
