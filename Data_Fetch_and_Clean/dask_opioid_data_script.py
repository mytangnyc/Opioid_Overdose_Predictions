import dask.dataframe as dd
import pandas as pd

traintypes = {'BUYER_NAME': 'str',
              'BUYER_CITY': 'str',
              'BUYER_STATE': 'str',
              'BUYER_ZIP': 'int64',
              'BUYER_COUNTY': 'str',
              'DRUG_NAME': 'str',
              'QUANTITY': 'int64',
              'UNIT': 'str',
              'TRANSACTION_DATE': 'int64',
              'CALC_BASE_WT_IN_GM': 'float64',
              'DOSAGE_UNIT': 'float64',
              'Product_Name': 'str',
              'Ingredient_Name': 'str',
              'Revised_Company_Name': 'str',
              'Reporter_family': 'str'}

cols = list(traintypes.keys())
interestingColumns = ['BUYER_STATE', 'BUYER_COUNTY','DRUG_NAME', 'DOSAGE_UNIT', 'TRANSACTION_DATE']
df = dd.read_csv(TRAIN_PATH,sep='\t', usecols=interestingColumns,dtype=traintypes)
TRAIN_PATH = "/home/bwood/Downloads/arcos_all_washpost.tsv"
df = dd.read_csv(TRAIN_PATH,sep='\t', usecols=interestingColumns,dtype=traintypes)

countydf['TRANSACTION_DATE'] = countydf['TRANSACTION_DATE'].astype(str).str[-4:]
df['TRANSACTION_DATE'] = df['TRANSACTION_DATE'].astype(str).str[-4:]

group = df.groupby(['BUYER_COUNTY', 'BUYER_STATE', 'TRANSACTION_DATE'])['DOSAGE_UNIT'].sum()
groupSort = group.compute().sort_values(ascending=False)

groupDF = pd.DataFrame(data=groupSort)
test = groupDF.reset_index()
test.head()
test[test['BUYER_COUNTY'] == 'CHARLESTON']
test[test['BUYER_COUNTY'] == 'CHARLESTON']['DOSAGE_UNIT'].sum()
test[test['BUYER_COUNTY'] == 'MINGO']['DOSAGE_UNIT'].sum()

test.to_csv('~/Downloads/Opiod_Sales_County_Year.csv')

