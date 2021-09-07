# fovt-data-pipeline

The fovt-data-pipeline contains scripts to process, reason, and load data for the FuTRES project.  Processed data is loaded into an ElasticSearch document store and made accessible to the [FuTRES query interface](https://futres-data-interface.netlify.app/) and the [FuTRES R package](https://github.com/futres/rfutres)  as well as populating summary statistics in driving the [FuTRES website dashboard](https://futres.org/).  This repository aggregates FuTRES trait data that has been loaded into [GEOME](https://geome-db.org/) as well as VertNet.  Detailed instructions on loading data into GEOME, using the FuTRES team, are provided on the [FuTRES website](https://futres.org/data_tutorial/).  Please note that this repository is designed to process millions of records from multiple repositories and is fairly complex.  To give interested users an idea of how the reasoning steps work, we have a provided a simple start section below demonstrating how this crucial part of the process works.  

*Credits: This codebase draws on the [Ontology Data Pipeline](https://github.com/biocodellc/ontology-data-pipeline) for triplifying and reasoning, the [FuTRES Ontology for Vertebrate Traits](https://github.com/futres/fovt) as the source ontology, and [ROBOT](http://robot.obolibrary.org/) as a contributing library for the reasoning steps.  Data processing scripts in assembling VertNet data extracts and getting legacy data ready for ingest into GEOME are stored at [fovt-data-mapping](https://github.com/futres/fovt-data-mapping)*

# Simple Start
To quickly test the validation, triplifying and reasoning steps, you can start here.

  * First, [Install docker](https://docs.docker.com/install/) and then clone this repository.  
  * Second, run the pipeline using the provided example:

```
# try the example script using Docker
./example.run.sh

# or, you can run this directly in python.  This assumes you checkout the ontology-data-pipeline code repository at the same level as ontology-data-pipeline
 python ../ontology-data-pipeline/pipeline.py -v --drop_invalid  sample_data_processed.csv sample_data/output https://raw.githubusercontent.com/futres/fovt/master/fovt.owl config
```

This example uses a file that has already been pre-processed, `sample_data_processed.csv`, and tagged with labels that exist in our ontology.  Output is stored in `sample_data/output` and uses processing directives stored in the `config` directory.

# Complete Process 
Here we follow the complete process for processing FuTRES data.  The steps below are completed sequentially with outputs from earlier steps being used as input to later steps.

## STEP 1: Pre-processing
Pre-processing functions to obtain data from remote sources and populating data tables that are used in the reasoning step.   This provides summary statistics for the [FuTRES website](https://futres.org/) as well as assembling all data sources into a single file in `data/futres_data_processed.csv`.  Importantly, this step reports any data that has been removed from the data set during processing into an error log: `data/futres_data_with_errors.csv`

### Installation
First, we need to setup our environment to be able to connect to remote local stores and setup our python working environment:

  * Copy dbtemp.ini to db.ini and update credentials locally
  * Ensure you are running python version of at least 3.6.8  Reccomend using pyenv to manage your environment, see https://github.com/pyenv/pyenv-virtualenv
  * pip install -r requirements.txt

Here is how to create a virtual environment specific to futres (assuming you already have setup pyenv):
```
# install a python version
pyenv install 3.7.2

# Create a virtual environment for futres-pyenv
pyenv virtualenv 3.7.2 futres-api

# automatically set futres-api to current directory when you navigate to this directory
pyenv local futres-api
```

### Fetching VertNet data
Vertnet data extracts are stored in a directory called `vertnet` immediately off of the root directory of this repository.
This directory is ignored in the .gitignore file.  You will need to first copy the VertNet data extracts from the CyVerse Discovery Environment. See [getDiscoveryEnvironmentData.md](getDiscoveryEnvironmentData.md) for instructions on coyping the VertNet data.

### Running the Script
The fetch.py script fetches data from GEOME and looks in the VertNet directory for
processed Vertnet data,  populating summary statistics as JSON files, and finally creates a single file to store all processed data as  `data/futres_data_processed.csv`.  This file is used by the reasoning pipeline in Step 2 below.  The fetch script is run using:

```
python fetch.py
```

The above script reports any data that has been removed from the data set during processing into an error log: `data/futres_data_with_errors.csv` and storing data at `data/futres_data_processed.csv`.

## STEP 2: Running the Reasoner
First, [Install docker](https://docs.docker.com/install/) and then clone this repository.  Once that is done, you can test
the environment by following the instructions under 'Simple Start' above.  This will verify that the reasoner is running correctly.
Run the ontology-data-pipeline using the input data file data/futres_data_processed.csv as input data,
data/output as the output directory and configuration files stored in the config directory.

```
# using docker
./run.sh data/futres_data_processed.csv data/output config

# using python and ontology-data-pipeline directly:
 python ../ontology-data-pipeline/pipeline.py -v --drop_invalid  data/futres_data_processed.csv data/output https://raw.githubusercontent.com/futres/fovt/master/fovt.owl config
```

An alternate way of running the reasoner, if you want to bypass docker and instead use python directly would be:

```
# 1. clone biocodellc/ontology-data-pipeline into ../ontology-data-pipeline
# 2. Run the following command:
python ../ontology-data-pipeline/pipeline.py -v --drop_invalid  data/futres_data_processed.csv data/output https://raw.githubusercontent.com/futres/fovt/master/fovt.owl config
```

*NOTE 1: you must reference your input data file to reason within the root-level heirarchicy of this repository. We have provided the `data/` directory for putting input and output data files, although you can use any directory under the root.
The docker image cannot find files like `../some-other-directory/file.txt`.*

*NOTE 2:  you may wish to run the reasoner using python directly instead of docker.  You can find a reference to that procedure by visiting the [ontology-data-pipeline repository](https://github.com/biocodellc/ontology-data-pipeline).*

## STEP 3: Loading Data

The `loader.py` script populates the elasticsearch backend database using the loader.py script.  The elastic search loader references the host, index, and directory to search for files directly in the script.  In cases where this repository is forked, these values can be changed directly in code. The following script looks for output in `data/output/output_reasoned_csv/data*.csv`

```
python loader.py
```

NOTE: since the size of the data can be quite large and the `loader.py` script sends uncompressed data, we probably want to send the files to a remote server from our desktop machine.  This command would look like:

```
tar zcvf - data/output/output_reasoned_csv/* | ssh USER@SOME.SERVER.COM  "cd /home/USER/data/futres; tar xvzf -"
```

## STEP 4: biscicol-server updates
The code over at [biscicol-server](https://biscicol.org/) has additional functions for serving the loaded FuTRES data living at the https://futres.org/ website, including:
  * updating fovt ontology lookups (with links to updating GEOME Controlled Vocabs) and dynamic links for generating ontology lookup lists for the FuTRES website
  * a nodejs script, under `scripts/futres.fetchall.js` for bundling all of FuTRES script into a single zip archive, handy for R work where you want to look at all of FuTRES data

# Application Programming Interface
This repository generates files in the pre-processing step which serve as an API.  These files are referenced at [https://github.com/futres/fovt-data-pipeline/blob/master/api.md].  In addition to this datasource, there is a dynamic data service which references files that were loaded into elasticsearch in the "Loading Data" step, above.  The FuTRES dynamic data is hosted by the plantphenology nodejs proxy service at:
https://github.com/biocodellc/ppo-data-server/blob/master/docs/es_futres_proxy.md   The following endpoints to that datastore are:

  *  [futresapi/v2/download_futres_proxy](https://github.com/biocodellc/ppo-data-server/blob/master/docs/download_futres_proxy.md) Query the Futres data store download_futres_proxy.md
  *  [futresapi/v1/query](https://github.com/biocodellc/ppo-data-server/blob/master/docs/es_futres_proxy.md) Query the Futres data store 
  *  [futresapi/v2/fovt](https://github.com/biocodellc/ppo-data-server/blob/master/docs/futres_ontology_proxy.md) Lookup terms from the FOVT ontology

 





