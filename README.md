# fovt-data-pipeline

This repository contains the configuration directives and necessary scripts to validate, triplify, reason, and load data into an external document store for the FuTRES project.  This repository uses data that has first been pre-processed using [data-mapping R Scripts](https://github.com/futres/fovt-data-mapping) and [GEOME](https://geome-db.org/) for validating data and reporting problem data.  Refer to the [data-mapping](https://github.com/futres/fovt-data-mapping) repository for more information.  Please note that this repository is designed to process millions of records from multiple repositories and is fairly complex.  We have a provided a simple start section below which demonstrates the reasoning steps used in producing the final output.  

This codebase draws on the [Ontology Data Pipeline](https://github.com/biocodellc/ontology-data-pipeline) for triplifying and reasoning, the [FuTRES Ontology for Vertebrate Traits](https://github.com/futres/fovt) as the source ontology, and [Ontopilot](https://github.com/stuckyb/ontopilot) as a contributing library for the reasoning steps.  

# Getting Started
## Simple Start
If you wish to quickly test the validation, triplifying and reasoning steps, you can start here.    
  * First, [Install docker](https://docs.docker.com/install/) and then clone this repository.  Once that is done, you can test
  * Second, run the pipeline using some provided examples, like  like this:
```
./run.sh sample_data_processed.csv data/output config
```
This example uses a file that has already been pre-processed (`sample_data_processed.csv`) and tagged with labels that exist in our ontology.  Output is stored in `data/output` and uses processing directives stored in the `config` directory.

## Complete process / Advanced
Here we follow the complete process for pre-processing and processing data for the API and formatting for the pipeline. 
 * Process data using the `fetch.py` script in this repository.  This provides summary statistics for the [FuTRES website](https://futres.org/) as well as assembling all data sources into a single file in `../FutresAPI/data/futres_data_processed.csv`.  Importantly, this step reports any data that has been removed from the data set during processing into an error log: `../FutresAPI/data/futres_data_with_errors.csv`
  * Run the pipeline code `run.sh data/futres_data_processed.csv data/output config`
  * Run the loader code to load data into elasticsearch `python loader.py`. This script looks for output in `data/output/output_reasoned_csv/data*.csv`


# Pre-processing: Assembling data and building API lookup Tables
## Installation
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

## Fetching vertnet data
Vertnet data extracts live in a directory called `vertnet` immediately off of the root directory of this repository.
This directory is ignored in the .gitignore file.  The [getDiscoveryEnvironmentData.md](getDiscoveryEnvironmentData.md) has
information on updating the vertnet dataset.

## Running the Script
The fetch.py script gets data from GEOME and looks in the vertnet directory for
processed Vertnet scripts and populates JSON files in the data directory as well
as the `data/futres_data_processed.csv` which is used by the reasoning pipeline below.

See api.md for the API documentation

# Running Triplifier and Reasoner using Docker
This is the reccomended route.
First, [Install docker](https://docs.docker.com/install/) and then clone this repository.  Once that is done, you can test
the environment by using the following script, which demonstrates calling docker and running the necessary commands.
It uses the provided `sample_data_processed.csv` file and a sample ontology:

```
./example.run.sh
# You will see some output text, ending with something like this:
...
INFO:root:reasoned_csv output at data/output/output_reasoned_csv/data_1.ttl.csv
```
*NOTE:* you must reference your input data file to reason within the root-level heirarchicy of this repository. We have provided the `data/` directory for putting input and output data files, although you can use any directory under the root.
The docker image cannot files like `../some-other-directory/file.txt`. 

The above script calls `run.sh` which executes a docker pull (to check for latest image), and then
runs the script in the local environment.  You can view the contents of run.sh using `more run.sh` to get an
idea of how to structure your own script if you choose.   For processing FuTRES data, we will want to place the output of the FuTRESAPI processing code into our `/data` directory as `/data/futres_data_processed.csv`

# Running with Python instead of Docker
You can also run scripts using python directly.  To do this:

  * clone the [ontology-data-pipeline](https://github.com/biocodellc/ontology-data-pipeline) repository and place at `../ontology-data-pipeline` 
  * clone the [ontopilot](https://github.com/stuckyb/ontopilot) repository and place at `../ontopilot` 
  * create a symbolic link in root directory of fovt-data-pipeline like `ln -s ../ontopilot ontopilot` (this is required for referencing in the reasoner step)

Once you have completed the above steps, you can run the following, substituting your input data file (replacing `sample_data_processed.csv`) when you are ready:

```
# a sample_runner script running python directly assuming that you have ontology-data-pipeline checked out
# in the proper location
    python ../ontology-data-pipeline/process.py \
    -v --drop_invalid \
    sample_data_processed.csv \
    data/output \
    https://raw.githubusercontent.com/futres/fovt/master/fovt.owl \
    config \
```
For processing FuTRES data, we will want to place the output of the FuTRESAPI processing code into our `/data` directory as `/data/futres_data_processed.csv`

# Loading Data

The `loader.py` script populates the elasticsearch backend database using the loader.py script

The FuTRES dynamic data is hosted by the plantphenology nodejs proxy service at:
https://github.com/biocodellc/ppo-data-server/blob/master/docs/es_futres_proxy.md

 





