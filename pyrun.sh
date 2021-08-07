#!/bin/bash
PYENV_VERSION=futres-api
INPUT_DATAFILE=$1
OUTPUT_DIRECTORY=$2
CONFIG=$3
ONTOLOGY=https://raw.githubusercontent.com/futres/fovt/master/fovt.owl

if [[ -z $INPUT_DATAFILE ]] || [[ -z $OUTPUT_DIRECTORY ]]|| [[ -z $CONFIG ]]
   then
     echo "Usage: pyrun.sh {DATAFILE} {OUTPUT_DIRECTORY} {CONFIG}"
     echo ""
     echo "This bash script runs the pipeline for any INPUT_DATAFILE and places output in the specified OUTPUT_DIRECTORY." 
     echo "It executes the PYTHON code for ontology-data-pipeline and should only be run if you have the ontology-data-pipeline"
     echo "running and installed on your computer in the proper location. This script is only for testing purposes"
     echo ""
     exit 0
fi

echo " python ../ontology-data-pipeline/pipeline.py -v --drop_invalid " $INPUT_DATAFILE $OUTPUT_DIRECTORY  $ONTOLOGY  $CONFIG 

python ../ontology-data-pipeline/pipeline.py \
-v --drop_invalid \
$INPUT_DATAFILE \
$OUTPUT_DIRECTORY \
$ONTOLOGY \
$CONFIG \
