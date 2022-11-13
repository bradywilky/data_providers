import pandas as pd

import requests
import json
import os

from utils import StepTimer


def _get_acled_dataframe(url):

    with requests.Session() as s:
        download = s.get(url)

    decoded_content = download.content.decode('utf-8')

    res = json.loads(decoded_content)
    data = res['data']

    return pd.DataFrame(data)

# THESE PARAMETERS MUST BE IN A SPECIFIC FORMAT
    # limit: integer of desired row limit in dataframe
    # date (str): YYYY-MM-DD
    # date_range (str): YYYY-MM-DD:AND:YYYY-MM-DD
    # region (int): Numeric ID for desired region

# THESE PARAMETERS USE 'LIKE' IN ACLED REQUEST BACKEND, SO THEY DO NOT HAVE TO BE EXACT.
    # source (str)
    # source_scale (str)
    # event_type (str)
    # notes (str)

def _get_url(
    limit=100,
    date=None,
    date_minimum=None,
    date_maximum=None,
    region=None,
    source=None,
    source_scale=None,
    event_type=None,
    sub_event_type=None,
    notes=None
):
   
    email = 'bwilki13@gmu.edu'
    acled_key = 'fTIpbk9YOV5PYNcjf3v3'
    
    url = f'https://api.acleddata.com/acled/read?key={acled_key}&email={email}'
    
    filters = f'&limit={limit}'
    if date:
        filters += f'&event_date={date}'
    if date_minimum or date_maximum:
        filters += f'&event_date:BETWEEN:{date_minimum}:AND:{date_maximum}'
    if region:
        filters += f'&region={region}'
    if source:
        filters += f'&source={source}'
    if source_scale:
        filters += f'&source_scale={source_scale}'
    if event_type:
        filters += f'&event_type={event_type}'
    if sub_event_type:
        filters += f'&sub_event_type={sub_event_type}'
    if notes:
        filters += f'&notes={notes}'
    
    return url + filters
    
def pull_acled_data(date_minimum, date_maximum):
        
    
    url = _get_url(
        limit=1000000,
        notes='coronavirus',
        date_minimum = date_minimum,
        date_maximum = date_maximum
        )
    cor_df = _get_acled_dataframe(url)

    url = _get_url(
        limit=1000000,
        notes='COVID-19',
        date_minimum = date_minimum,
        date_maximum = date_maximum
        )
    cov_df = _get_acled_dataframe(url)

    df_raw = pd.concat([cor_df, cov_df])
    df = df_raw.drop_duplicates()
    
    return df
    
    
def read_local(path):
    try:
        return pd.read_csv(path)
    except:
        print(f'Data cannot be found at the provided path {local_data_path}')
        
        
def write_local(df, suffix, name, path = os.getcwd()):

    name_suffix = f'{name}.{suffix}'
    
    if suffix == 'csv':
        df.to_csv(os.path.join(path, name_suffix))
        
    elif suffix == 'json':
        df.to_json(os.path.join(path, name_suffix))
    else:
        print(f'Cannot save tagged data as a {suffix}.')