import pandas as pd
import numpy as np
from pandasql import sqldf
from sklearn.cluster import KMeans


# helper function to create a dataframe with each source and the number of times the source has been used by ACLED
def _get_tot_cnt_df(df):
    sql = lambda q: sqldf(q, locals())
    
    tot_cnt_df = sqldf(f'''
        SELECT source_singular,
        count(*) total
        FROM df
        GROUP BY source_singular
    ''', locals())
    
    return tot_cnt_df
    
    
# helper function to modify column names to work with pandasql
def _clean(c):
    for r in [' ', '-', '/']:
        c = c.replace(r, '_')
    
    for r in ['.', ',']:
        c = c.replace(r, '')
    
    return c


# filter dataframe to get tags for each source that meet the criteria to be a tag
# params:
#  tag_col: name of column to use as tag
#  dst_df: df of distinct tagging values (required for SQL)
#  type_pct_df: df of the percents of each tag in each source (required for SQL)
#  total_min: the minimum number of times the source has been used by ACLED
#  total_max: the maximum number of times the source has been used by ACLED
#  pct_min: the minimum percent of events per source required to be from the tag value

def _generate_tag_df(tag_col, dst_df, type_pct_df, total_min, total_max, pct_min):
    # required for pandasql to work properly
    type_pct_df_sql = type_pct_df
    
    # creating empty dataframe for each source, potential tag value, total times used with the potential tag value,
    # and percentage of times used with the potential tag value
    df = pd.DataFrame(columns=[
        'source_singular',
        tag_col,
        f'{tag_col}_total',
        f'{tag_col}_pct'
    ])
    
    # iterating through every potential tag value and appending candidate tagged sources to the empty dataframe
    for t in dst_df[tag_col]:
        t_cln = _clean(t)
        t_cln_pct_nm = t_cln + '_pct'

        query = f'''
        SELECT
            source_singular,
            "{t_cln}_majority" AS "{tag_col}",
            {t_cln} AS "{tag_col}_total",
            {t_cln_pct_nm} AS {tag_col}_pct
        FROM
            type_pct_df
        WHERE 
            total >= {total_min}
            AND total <= {total_max}
            AND {t_cln_pct_nm} >= {pct_min}
        '''

        df1 = sqldf(query, locals())
        df = pd.concat([df, df1])
        
    # returning dataframe of sources and candidate tags 
    return df


# takes extended DF as parameter
def tag_sub_event_type(df, total_min, total_max, pct_min):

    # getting distinct list of specific event types from the "sub_event_type" column
    typ_df = sqldf('''
        SELECT DISTINCT sub_event_type
        FROM df
    ''', locals())

    # generating query to get binary indicators for each sub_event_type
    query_fmt = ''
    for i, t in enumerate(typ_df['sub_event_type']):
        t_cln = t.replace(" ", "_")
        t_cln = t_cln.replace("/", "_")
        query_fmt += f'sum(CASE WHEN sub_event_type = "{t}" THEN 1 ELSE 0 END ) AS "{t_cln}"'
        if i < len(typ_df['sub_event_type']) - 1:
            query_fmt += ',\n'

    # applying above query
    type_cnt_df = sqldf(f'''
        SELECT source_singular,
        {query_fmt}
        FROM df
        GROUP BY source_singular
    ''', locals())

    # getting dataframe of each source and the total of how many times the source was used by ACLED in an event
    tot_cnt_df = _get_tot_cnt_df(df)
    
    # generating query to get percent of sub_event_type reported on by each source for each sub_event_type
    query_fmt = ''
    for i, t in enumerate(typ_df['sub_event_type']):
        t_cln = t.replace(" ", "_")
        t_cln = t_cln.replace("/", "_")
        t_cln_pct_nm = t_cln + '_pct'
        query_fmt += f'cast({t_cln} AS DOUBLE) / cast(total AS DOUBLE) "{t_cln_pct_nm}"'
        if i < len(typ_df['sub_event_type']) - 1:
            query_fmt += ',\n'

    # applying above query
    type_pct_df = sqldf(f'''
        SELECT
            a.*,
            b.total,
            {query_fmt}
        FROM type_cnt_df a
        JOIN tot_cnt_df b
            ON a.source_singular = b.source_singular
    ''', locals())

    # filter dataframe to get sub_event_type for each source that meet the criteria to be a tag
    sub_event_type_df = _generate_tag_df('sub_event_type', typ_df, type_pct_df, total_min, total_max, pct_min)
    
    return sub_event_type_df



# takes extended DF as parameter
def tag_country(df, total_min, total_max, pct_min):

    # getting distinct list of geographical locations (countries) from the "country" column
    geo_df = sqldf('''
        SELECT DISTINCT country
        FROM df
    ''', locals())

    # generating query to get binary indicators for each country
    query_fmt = ''
    for i, t in enumerate(geo_df['country']):
        t_cln = _clean(t)
        query_fmt += f'sum(CASE WHEN country = "{t}" THEN 1 ELSE 0 END ) AS "{t_cln}"'
        if i < len(geo_df['country']) - 1:
            query_fmt += ',\n'

    # applying above query
    type_cnt_df = sqldf(f'''
    SELECT source_singular,
    {query_fmt}
    FROM df
    GROUP BY source_singular
    ''', locals())
    
    # getting dataframe of each source and the total of how many times the source was used by ACLED in an event
    tot_cnt_df = _get_tot_cnt_df(df)
    
    # generating query to get percent of countries reported on by each source for each country
    query_fmt = ''
    for i, t in enumerate(geo_df['country']):
        t_cln = _clean(t)
        t_pct_nm = t_cln + '_pct'
        query_fmt += f'cast({t_cln} AS DOUBLE) / cast(total AS DOUBLE) "{t_pct_nm}"'
        if i < len(geo_df['country']) - 1:
            query_fmt += ',\n'
    
    # applying above query
    type_pct_df = sqldf(f'''
    SELECT
        a.*,
        b.total,
    {query_fmt}
    FROM type_cnt_df a
    JOIN tot_cnt_df b
        ON a.source_singular = b.source_singular
    ''', locals())
    
    # filter dataframe to get countries for each source that meet the criteria to be a tag
    cntry_df = _generate_tag_df('country', geo_df, type_pct_df, total_min, total_max, pct_min)
    
    return cntry_df


# takes extended DF as parameter
def tag_time_period(df, n_clusters=4, init='random', n_init=10, max_iter=100, tol=1e-04, random_state=0):
    # setting up K-Means clustering model to identify time periods to tag the data with
    km = KMeans(
        n_clusters=n_clusters, init=init,
        n_init=n_init, max_iter=max_iter,
        tol=tol, random_state=random_state
    )
    
    # creating df that will be clustered by "event_date"
    cluster_df = df
    
    # creating column transforming event_date to a unix timestamp for the clustering algorithm to work
    cluster_df.event_date_unix = cluster_df['event_date'].apply(lambda x: pd.Timestamp(x).timestamp())

    # reshaping to fit clustering algorithm requirements and fitting model
    X = np.array(cluster_df.event_date_unix).reshape(-1, 1)
    y_km = km.fit_predict(X)

    # appending cluster labels back to df
    cluster_df['time_period'] = y_km
    
    # selecting only required columns for returned df
    cluster_df = cluster_df[['source_singular', 'time_period']]
    
    return cluster_df


def tag_data(df, thresholds):
    base_df = df[['source_singular']].drop_duplicates()
    base_df = base_df.rename({'source_singular': 'source_singular_main'}, axis=1)
    
    for tag_df in [
        tag_country(df, thresholds['cty_min'], thresholds['cty_max'], thresholds['cty_pct']),
        tag_sub_event_type(df, thresholds['evt_min'], thresholds['evt_max'], thresholds['evt_pct'])
    ]:
        
        base_df = sqldf('''
            SELECT * FROM base_df a
            LEFT JOIN tag_df b ON a.source_singular_main = b.source_singular
        ''', locals())
  

    return base_df