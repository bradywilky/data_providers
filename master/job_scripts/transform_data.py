import pandas as pd

from pandasql import sqldf


def expand_source_data(df):

# First, we get a collective list of sources
    sources_list = list()
    for s in df['source']:
        for i in s.split(';'):
            sources_list.append(i.strip())
            
    # From our collective list of sources we need a pandas DataFrame of distinct sources
    sources_distinct = list(set(sources_list))
    sources_distinct_df = pd.DataFrame({'source_singular': sources_distinct})

    # since eventually we're using a LIKE clause for the join, we need to add percentage wildcards around each distinct source
    # here in our pandas DataFrame, because we can't in pandasql.
    sources_distinct_df['source_singular'] = sources_distinct_df['source_singular'].apply(lambda x: f'%{x}%')

    # Second, join this distinct source df with the main df. I prefer using pandasql because of the LIKE clause.

    expanded_source_df = sqldf(
    '''
        SELECT * FROM df main
        JOIN sources_distinct_df dst_src
        ON main.source LIKE dst_src.source_singular
    ''', locals()
    )

    # We can now remove the percentage wildcards from the source_singular column, since we only needed them for the previous step.
    expanded_source_df['source_singular'] = expanded_source_df['source_singular'].apply(lambda x: x.replace('%', ''))
    
    # Some sources do not correctly join, so we remove them.
    expanded_source_df['source_list'] = expanded_source_df['source'].str.split(';')
    
    final_expanded_source_df = expanded_source_df[
        expanded_source_df.apply(lambda x: x.source_singular in [s.strip() for s in x.source_list], axis=1)
    ]
    
    final_expanded_source_df = final_expanded_source_df.drop('source_list', axis=1)
    
    return final_expanded_source_df