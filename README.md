# About data_providers repository

This repository hosts the code that aims to create metadata tags for sources from COVID-19-related data from the [Armed Conflict Location & Event Data Project (ACLED)](https://acleddata.com/about-acled/). When a civil conflict occurs, data collectors from ACLED log it as an event in the dataset. One or more news articles are used as sources of information for the various data attributes, including event type (peaceful protest, armed conflict, etc.), geolocation (countries, regions, and cities), and date of occurrence. We aim to create metadata tags for the sources based on "usage", or how ACLED used the various sources in adding to their dataset.


# Structure
The repository is separated by two directories: **code_development** and **master**. The **master** directory hosts the Python scripts that ingest, transform, tag, and output the data. The **code_development** directory, holds the Jupyter notebooks where code was developed. The job runs from the Bash script at **bash/bin/run_job.sh**, where the user can provide optional parameters (outlined in run instructions). The job runs various functions consolidated in the Python script **master/main.py**. This script utilizes functions from the other Python scripts in the **master** directory.

# Run instructions
The run instructions are outlined below:

1. Ensure that Python 3+ is installed and can be found on your PATH variable
2. Navigate to the **data_providers** repository
3. Identify what optional parameters you want to specify. The job can also run on default parameters
  - `date_minimum`**:** The earliest an event can occur in the format %Y%m%d
  - `date_maximum`**:** The latest an event can occur in the format %Y%m%d
  - `tag_local`**:** Specify `True` if you want to tag a dataset from a local directory
  - `local_data_path`**:** The local directory you want to tag a dataset from
  - `tagged_data_output_path`**:** The local path you want to save the tagged data at
  - `tagged_data_output_name`**:** The name of the tagged data to save
  - `tagged_data_format_suffix`**:** The format of the tagged data file. Can be either a JSON or a CSV file
4. Run the command `. /master/bin/run_job.sh`

# Job steps
The job will output how long each step in the job took in between the messages "starting job..." and "job finished". Each step is outlined below:
1. Ingest
  - The data is read as a Pandas `DataFrame` object from either ACLED's data API or read from a specified local file.
  - `ingest_data.py`
2. Transform
  - The `DataFrame` object is transformed by creating distinct rows for each source per event.
  - `transform_data.py`
3. Tag
  - Tags are dynamically generated based on the contents of the transformed `DataFrame` object. These tags are appended to their respective distinct sources as a new `DataFrame` object.
  - `tag_data.py`
4. Save
  - The new tagged `DataFrame` object is saved at either the default or specified location as a CSV or JSON, if specified.
  - `ingest_data.py`


# Authors
bradywilky
mvaid2
pdasari
saibharath123
sbade