# fovt-data-pipeline

This repository contains the configuration directives and necessary scripts to validate, reason, and load data into an external document store for the FuTRES project as well as populating summary statistics in driving the [FuTRES website](https://futres.org/).  This repository uses data that has first been pre-processed using [data-mapping R Scripts](https://github.com/futres/fovt-data-mapping) and [GEOME](https://geome-db.org/) for validating data and reporting problem data.  Refer to the [data-mapping](https://github.com/futres/fovt-data-mapping) repository for more information.  Please note that this repository is designed to process millions of records from multiple repositories and is fairly complex.  We have a provided a simple start section below which demonstrates the reasoning steps used in producing the final output.  

This codebase draws on the [Ontology Data Pipeline](https://github.com/biocodellc/ontology-data-pipeline) for triplifying and reasoning, the [FuTRES Ontology for Vertebrate Traits](https://github.com/futres/fovt) as the source ontology, and [Ontopilot](https://github.com/stuckyb/ontopilot) as a contributing library for the reasoning steps. 

# Simple Start
If you wish to quickly test the validation, triplifying and reasoning steps, you can start here.    
  * First, [Install docker](https://docs.docker.com/install/) and then clone this repository.  Once that is done, you can test
  * Second, run the pipeline using some provided examples, like  like this:
```
./run.sh sample_data_processed.csv data/output config
```
This example uses a file that has already been pre-processed (`sample_data_processed.csv`) and tagged with labels that exist in our ontology.  Output is stored in `data/output` and uses processing directives stored in the `config` directory.

# Complete Process 
Here we follow the complete process for processing FuTRES data.  It begins with fetching data from GEOME and VertNet.  The steps below are completed sequentially with outputs from earlier steps, used to feed into outputs from later steps.

## STEP 1: Pre-processing
Pre-processing functions to obtain data from remote sources and populating data tables that are used in the reasoning step.   This provides summary statistics for the [FuTRES website](https://futres.org/) as well as assembling all data sources into a single file in `data/futres_data_processed.csv`.  Importantly, this step reports any data that has been removed from the data set during processing into an error log: `data/futres_data_with_errors.csv`

### Installation
First, we need to setup our environment to be able to connect to remote local stores and setup our python working environment:

  * Copy dbtemp.ini to db.ini and update credentials locally
  * Ensure you are running python version of at least 3.6.8  Reccomend using pyenv to manage your environment, see https://github.com/pyenv/pyenv-virtualenv
  * pip install -r requirements.txt

Here is how to create a virtual environment specific to futres (assuming you already have setup pyenv):
```
# Create a virtual environment for futres-pyenv
pyenv virtualenv 3.7.2 futres-api

# automatically set futres-api to current directory when you navigate to this directory
pyenv local futres-api
```

### Fetching vertnet data
Vertnet data extracts live in a directory called `vertnet` immediately off of the root directory of this repository.
This directory is ignored in the .gitignore file.  The [getDiscoveryEnvironmentData.md](getDiscoveryEnvironmentData.md) has
information on updating the vertnet dataset.

### Running the Script
The fetch.py script gets data from GEOME and looks in the vertnet directory for
processed Vertnet scripts and populates JSON files in the data directory as well
as the `data/futres_data_processed.csv` which is used by the reasoning pipeline below.
The fetch script is run using:

```
python fetch.py
```
The above script reports any data that has been removed from the data set during processing into an error log: `data/futres_data_with_errors.csv` and storing data at `data/futres_data_processed.csv`.

## STEP 2: Running the Reasoner
First, [Install docker](https://docs.docker.com/install/) and then clone this repository.  Once that is done, you can test
the environment by using the following script, which demonstrates calling docker and running the necessary commands. 

```
# This script executes a docker pull (to check for the latest image), and then runs the script in the local environment,
# using the provided `sample_data_processed.csv` file and a sample ontology:

./example.run.sh

# You will see some output text, ending with something like this:
...
INFO:root:reasoned_csv output at data/output/output_reasoned_csv/data_1.ttl.csv
```

After testing the reasoner using the command above, you can run the pipeline code using:

```
# run ontology-data-pipeline using the input data file data/futres_data_processed.csv as input data,
# data/output as the output directory and configuration files stored in the config directory.

./run.sh data/futres_data_processed.csv data/output config
```

*NOTE 1:* you must reference your input data file to reason within the root-level heirarchicy of this repository. We have provided the `data/` directory for putting input and output data files, although you can use any directory under the root.
The docker image cannot find files like `../some-other-directory/file.txt`. 

*NOTE 2:*  you may wish to run the reasoner using python directly instead of docker.  You can find a reference to that procedure by visiting the [ontology-data-pipeline repository](https://github.com/biocodellc/ontology-data-pipeline).

## STEP 3: Loading Data

The `loader.py` script populates the elasticsearch backend database using the loader.py script.  The elastic search loader references the host, index, and directory to search for files directly in the script.  In cases where this repository is forked, these values can be changed directly in code.

```
# this script looks for output in `data/output/output_reasoned_csv/data*.csv`

python loader.py
```


# Application Programming Interface
This repository generates files in the pre-processing step which serve as an API.  These files are referenced at [https://github.com/futres/fovt-data-pipeline/blob/master/api.md].  In addition to this datasource, there is a dynamic data service which references files that were loaded into elasticsearch in the "Loading Data" step, above.  The FuTRES dynamic data is hosted by the plantphenology nodejs proxy service at:
https://github.com/biocodellc/ppo-data-server/blob/master/docs/es_futres_proxy.md   The following endpoints to that datastore are:

  *  [futresapi/v2/download_futres_proxy](https://github.com/biocodellc/ppo-data-server/blob/master/docs/download_futres_proxy.md) Query the Futres data store download_futres_proxy.md
  *  [futresapi/v1/query](https://github.com/biocodellc/ppo-data-server/blob/master/docs/es_futres_proxy.md) Query the Futres data store 
  *  [futresapi/v2/fovt](https://github.com/biocodellc/ppo-data-server/blob/master/docs/futres_ontology_proxy.md) Lookup terms from the FOVT ontology

 





