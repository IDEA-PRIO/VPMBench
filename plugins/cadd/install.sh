#!/usr/bin/env bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

echo "INSTALLING CADD"
echo "==============="
echo ""

echo "> Build Docker Image"
cd $BASEDIR/phred/
docker build -t vpmbench/cadd .

cd ..

echo "> Download Files (Approx. 200GB)"
wget -c https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh37/whole_genome_SNVs.tsv.gz.md5
wget -c https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh37/whole_genome_SNVs.tsv.gz.tbi.md5
wget -c https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh37/annotationsGRCh37_v1.6.tar.gz.md5

wget -c https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh37/annotationsGRCh37_v1.6.tar.gz
wget -c https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh37/whole_genome_SNVs.tsv.gz
wget -c https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh37/whole_genome_SNVs.tsv.gz.tbi

echo "> Check downloaded files"
md5sum -c *.md5
if [ $? -ne 0 ]; then
  echo "SOMETHING SEEMS WRONG WITH THE DOWNLOADED FILES!"
  echo "Compare the md5sum of the files."
  echo "Maybe re-downloading the file helps "
  echo "After re-downloading you have to tar -zxf annotationsGRCh37_v1.6.tar.gz"
  exit 1
fi

echo "> Extract annotations"
tar -zxf annotationsGRCh37_v1.6.tar.gz
rm annotationsGRCh37_v1.6.tar.gz
