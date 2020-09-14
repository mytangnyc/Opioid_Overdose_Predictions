import pandas as pd
import numpy as np
import geopandas as gpd
import xml.etree.ElementTree as ET
from scipy.spatial import cKDTree

def ckdnearest(gdA, gdB):
    nA = np.array(list(zip(gdA.centroid.x, gdA.centroid.y)) )
    nB = np.array(list(zip(gdB.centroid.x, gdB.centroid.y)) )
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=5)
    tuple_list = [dist, idx]
    return tuple_list


def impute_values(vals_df, shape_df, year, col_imp, wtg_avg):
    df_year = vals_df[vals_df['yr']==year]
    dict_vals_drugs_all = dict(zip(df_year['fips_code_str'], df_year[col_imp]))
    dict_vals_wtg = dict(zip(df_year['fips_code_str'], df_year[wtg_avg]))

    #Find the excluded counties that are missing in our data vs. the shapefiles
    all_fips = set(shape_df['fips'])
    found_in_excel = set(df_year['fips_code_str'].unique())
    diff = all_fips - found_in_excel
    diff = list(diff)

    #Find the counties with missing data from our spreadsheet
    missing_fips = df_year[df_year[col_imp].isnull()].fips_code_str
    missing_fips = set(missing_fips) #Get unique fips values

    missing_fips = list(missing_fips) #Change missing fips values to a list and add excluded county fips
    missing_fips.extend(diff)
    missing_fips.sort()

    #Separate countires into those missing data or excluded, and the remaining counties with data.
    missing_counties = shape_df[shape_df['fips'].isin(missing_fips)].copy(deep=True)
    missing_counties = missing_counties.reset_index()
    remaining_counties = shape_df[~shape_df['fips'].isin(missing_fips)]

    nn = ckdnearest(missing_counties, remaining_counties) #Spatial kNN via KDTree
    
    fips_avg = []
    for i in nn[1]:
        avg_list = []
        wtg_list = []
        for j in range(len(i)):
            indx = i[j]
            col = shape_df.columns.get_loc('fips')
            nearby_fip = remaining_counties.iloc[indx][col]
            drugs_related = dict_vals_drugs_all.get(nearby_fip, np.nan) #Extract drugs_all val from ML sheet
            wtg_related = dict_vals_wtg.get(nearby_fip, np.nan) #Extract wtg val (population weight for instance) from ML sheet
            avg_list.append(drugs_related*wtg_related)
            wtg_list.append(wtg_related)
        weighted_avg = np.nanmean(avg_list) / np.nansum(wtg_list)
        fips_avg.append(weighted_avg)

    #Add 3 more columns to the missing_counties dataframe
    missing_counties['nn_distances']=pd.Series((x for x in nn[0]))
    missing_counties['nn_rem_counties_indx']=pd.Series((x for x in nn[1]))
    missing_counties['nn_avg']=pd.Series((x for x in fips_avg))
    
    dict_fips_vals = dict(zip(missing_counties['fips'], missing_counties['nn_avg']))
    
    #Choose one of the below options
    #--------------------------------------------------------------------------#
    #1. Add values to separate column in Excel sheet
    #col_heading = 'imputed_'+str(year)+'_'+str(col_imp)+'_wtg_'+str(wtg_avg) #Add new Columns for each year's imputed values
    #df_year['imputed'] = pd.Series(df_year['fips_code_str'].map(dict_fips_vals))

    #--------------------------------------------------------------------------#
    #2. Add values to existing columns in Excel sheet
    col_heading = col_imp #Update imputed values in existing columns
    df_year['imputed'] = df_year['fips_code_str'].map(dict_fips_vals).fillna(df_year[col_imp])
    
    vals_df.loc[df_year.index,col_heading] = df_year.loc[df_year.index,'imputed']

    return vals_df


#Choose year, col, wtg_avg columns
#--------------------------------------------------------------------------#
#Load the ML dataframe and column to include
df = pd.read_csv("data/mlview_new_dup_removal.csv")
year = [2006,2007,2008,2009,2010,2011,2012] #Choose Number of Years
col = ['drugs_all','sale_synthetics'] #Choose columns to impute
wtg_avg = ['population'] #Choose Weighting (i.e. population weighted)

#Load the US shapefiles
def exclude_fip(desc):
    tree = ET.fromstring(desc)
    text_vals = [elem.text for elem in tree.iter()]
    state_fp = text_vals[text_vals.index('STATEFP')+1]
    if state_fp in excluded_state_fps: return True
    else: return False

def extract_fip(desc):
    tree = ET.fromstring(desc)
    text_vals = [elem.text for elem in tree.iter()]
    state_fp = text_vals[text_vals.index('STATEFP')+1]
    county_fp = text_vals[text_vals.index('COUNTYFP')+1]
    fip = str(state_fp) + str(county_fp)
    return fip
    
kml_file = 'shape_files/cb_2018_us_county_500k.kml'
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
df_shape = gpd.read_file(kml_file, driver='KML')
excluded_state_fps = ['60','66','69', '72', '78'] #Exclude American Samoa, Guam, Puerto Rico, and Virgin Islands
df_shape['exclude'] = df_shape['Description'].apply(exclude_fip)
df_shape=df_shape[df_shape['exclude']==False]
df_shape['centroid'] = df_shape.centroid
df_shape['fips'] = df_shape['Description'].apply(extract_fip)


#Add column changing fips to a 5 digit string
df['fips_code_str'] = df['fips_code'].apply(str)
df['fips_code_str'] = df['fips_code_str'].str.zfill(5)

#Impute Values
for y in year:
    for c in col:
        for w in wtg_avg:
            df_total = impute_values(df, df_shape, y, c, w)

df_total.to_csv('imputed_data.csv')