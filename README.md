# fovt-data-pipeline

This repository contains the configuration directives and necessary scripts to validate, triplify, reason, and load data into an external document store for the FuTRES project.  This repository uses data that has first been pre-processed using R Scripts and [GEOME](https://geome-db.org/) for validating data and reporting problem data.  Once the data has been pre-processed, this pipeline uses additional python code for further validation and API creation, the [Ontology Data Pipeline](https://github.com/biocodellc/ontology-data-pipeline) to direct post-processing steps, [FuTRES Ontology for Vertebrate Traits](https://github.com/futres/fovt) as the source ontology, and [Ontopilot](https://github.com/stuckyb/ontopilot) as a contributing library for the reasoning steps.  Configuration directives are stored in the `config/` directory.  If you want to modify configuration settings, refer to [ontology-data-pipeline](https://github.com/biocodellc/ontology-data-pipeline) for instructions.

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

# A summary of processing steps for FuTRES Data

The following steps describe the entire loading/process pipeline for FuTRES data.  The user will need to verify and check all data sources following each step.  In addition, data loading (the very last step) must be run from a host that has direct access to the ElasticSearch data store.  We use the `biscicol.org` server for this.
  * Assemble data from sources and pre-process using [data-mapping R scripts](https://github.com/futres/fovt-data-mapping)
  * Load data into [GEOME](https://geome-db.org/), which provides user feedback on data quality.  This does not include [VertNet](http://vertnet.org/) data sources, which have been processed separately.
  * Process data using the `fetch.py` script in this repository.  This provides summary statistics for the [FuTRES website](https://futres.org/) as well as assembling all data sources into a single file in `../FutresAPI/data/futres_data_processed.csv`.  Importantly, this step reports any data that has been removed from the data set during processing into an error log: `../FutresAPI/data/futres_data_with_errors.csv`
  * Run the pipeline code `run.sh data/futres_data_processed.csv data/output config`
  * Run the loader code to load data into elasticsearch `python loader.py`. This script looks for output in `data/output/output_reasoned_csv/data*.csv`





