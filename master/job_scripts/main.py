import os
import argparse

from datetime import datetime

from ingest_data import pull_acled_data, read_local, write_local
from transform_data import expand_source_data
from tag_data import tag_data

from utils import StepTimer


parser = argparse.ArgumentParser(
    description = 'Ingests data from ACLED, transforms the data to a tagged dataset by source'
)

parser.add_argument(
    '--date_minimum',
    help = 'Earliest date an event can occur on',
    default = None
)

parser.add_argument(
    '--date_maximum',
    help = 'Latest date an event can occur on',
    default = None
)

parser.add_argument(
    '--tag_local',
    help = 'Whether to tag local source of data rather than pulling from ACLED',
    default = False
)

parser.add_argument(
    '--local_data_path',
    help = 'Where to load local data to tag',
    default = None
)

parser.add_argument(
    '--tagged_data_output_path',
    help = 'Desired filepath to save tagged dataset',
    default = 'tagged_data'
)

parser.add_argument(
    '--tagged_data_output_name',
    help = 'What to name the data output as',
    default = f'tagged_data_{datetime.now().strftime("%d-%m-%Y_%H:%M:%S")}'
)

parser.add_argument(
    '--tagged_data_format_suffix',
    help = 'What format to save the data as',
    default = 'csv'
)


def main():

    args = parser.parse_args()

    date_minimum = args.date_minimum
    date_maximum = args.date_maximum
    tag_local = args.tag_local
    local_data_path = args.local_data_path
    tagged_data_format_suffix = args.tagged_data_format_suffix
    output_path = args.tagged_data_output_path
    output_name = args.tagged_data_output_name
    format_suffix = args.tagged_data_format_suffix
    
    
    if tag_local:
        with StepTimer('Reading local data'):
            df = read_local(local_data_path)
    else:
        with StepTimer('Reading data'):
            df = pull_acled_data(date_minimum, date_maximum)
        
    with StepTimer('Transforming data'):
        transformed_df = expand_source_data(df)
        
    with StepTimer('Tag data'):
        tagged_df = tag_data(transformed_df)

    with StepTimer(f'Saving tagged data as {os.path.join(output_path, output_name)}.{format_suffix}'):
        write_local(tagged_df, output_path, output_name, format_suffix)


if __name__ == '__main__':
    main()