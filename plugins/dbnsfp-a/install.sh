#!/usr/bin/env bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

echo "INSTALLING DBNSFP"
echo "==============="
echo ""

echo "> Download Files (Approx. 33GB)"
wget -c https://snpeff.blob.core.windows.net/databases/dbs/GRCh37/dbNSFP_4.1a/dbNSFP4.1a.txt.gz
wget -c https://snpeff.blob.core.windows.net/databases/dbs/GRCh37/dbNSFP_4.1a/dbNSFP4.1a.txt.gz.tbi
