#!/bin/bash
PYENV_VERSION=futres-api
ONTOLOGY=https://raw.githubusercontent.com/futres/fovt/master/fovt.owl

echo " python ../ontology-data-pipeline/pipeline.py -v --drop_invalid " $INPUT_DATAFILE $OUTPUT_DIRECTORY  $ONTOLOGY  $CONFIG 

python3 ../ontology-data-pipeline/pipeline.py \
-v --drop_invalid \
sample_data_processed.csv \
sample_data/output \
$ONTOLOGY \
config \
