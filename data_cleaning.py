# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 21:41:59 2021

@author: dakot
"""


import pandas as pd
import sqlite3
import regex as re
#from sklearn.model_selection import train_test_split
from mlxtend.preprocessing import minmax_scaling



#Call trulia web scraper to scrape data from trulia link and save to SQLite .db file
#This takes ~1-1.5 minutes per listing
'''
import trulia_web_scraper as tws
base_link="http://www.trulia.com/sold/Santa_Barbara,CA/SINGLE-FAMILY_HOME_type/"
num_pages=30

df=tws.web_scraper(base_link,num_pages)

conn = sqlite3.connect('ENTER_FILE_PATH')
df.to_sql(name='trulia_house_summary_data',con=conn,schema='raw_trulia_data.db',if_exists='replace') 
'''

#Query raw trulia house data from SQLite database

conn = sqlite3.connect('C:/Users/dakot/Desktop/DataScience/projects/dakota_portfolio/santa_barbara_realestate_analysis/trulia_sb_house_data.db')

houses_dataframe = pd.read_sql_query("SELECT * FROM trulia_house_SB_raw_data", conn)

#summarize missing values and total samples for raw data

missing_values_count=houses_dataframe.isnull().sum()

print('___RAW DATA SUMMARY____')

print(missing_values_count)

print("number of samples: "+str(len(houses_dataframe)))

#Turn year built into house age

houses_dataframe['house_age']=houses_dataframe['year_built'].apply(lambda x: 2022-x)

#rescale price to millions

houses_dataframe['price']=houses_dataframe['price'].apply(lambda x: x/(1e6))

#rescale sqft to thousands of sqft

houses_dataframe['building_sqft']=houses_dataframe['building_sqft'].apply(lambda x: x/(1000))

#Extract garage boolean from description

houses_dataframe['has_garage']=houses_dataframe['home_description'].apply(lambda x: 1 if 'garage' in x.lower() else 0)

#extract fireplace boolean from description

houses_dataframe['has_fireplace']=houses_dataframe['home_description'].apply(lambda x: 1 if 'fireplace' in x.lower() else 0)

#Extract ocean views boolean from description

houses_dataframe['has_ocean_views']=houses_dataframe['home_description'].apply(lambda x: 1 if 'ocean view' in x.lower() else 0)

#Extract mountian views boolean from description

houses_dataframe['has_mountain_views']=houses_dataframe['home_description'].apply(lambda x: 1 if 'mountain view' in x.lower() else 0)

# Extract hope ranch boolean from description

houses_dataframe['has_hope_ranch']=houses_dataframe['home_description'].apply(lambda x: 1 if 'hope ranch' in x.lower() else 0)

# Extract montecito boolean from description

houses_dataframe['has_montecito']=houses_dataframe['home_description'].apply(lambda x: 1 if 'montecito' in x.lower() else 0)

# Extract pool boolean from description

houses_dataframe['has_pool']=houses_dataframe['home_description'].apply(lambda x: 1 if 'pool' in x.lower() else 0)

# Extract upstair boolean from description

houses_dataframe['has_upstairs']=houses_dataframe['home_description'].apply(lambda x: 1 if ('upstair' in x.lower() or 'upstairs' in x.lower()) else 0)

#drop rows with missing values for price, num_baths, lot area, and year built

houses_dataframe['has_IV']=houses_dataframe['home_description'].apply(lambda x: 1 if 'isla vista' in x.lower() else 0)

#drop rows with missing values for price, num_baths, lot area, and year built

houses_dataframe.dropna(subset=['price','num_baths','lot_area','year_built'],inplace=True)

#drop rows with outlying prices (above 10 million)

houses_dataframe=houses_dataframe[houses_dataframe['price']<10]

#houses_dataframe=houses_dataframe[houses_dataframe['price']>0.9]

#drop rows with outlying land area (below 20 acres)

houses_dataframe=houses_dataframe[houses_dataframe['lot_area']<20]

#indicate if building sqft is missing for future imputation

houses_dataframe['building_sqft'+'_was_missing']=houses_dataframe['building_sqft'].isnull()

#summarize missing values and total samples for cleaned data

missing_values_count=houses_dataframe.isnull().sum()

print('___CLEANED DATA SUMMARY____')

print(missing_values_count)

print("number of samples: "+str(len(houses_dataframe)))

#Store cleaned data in new table is SQLite database
houses_dataframe.to_sql(name='trulia_house_SB_data_cleaned',con=conn,schema='trulia_sb_house_data.db',if_exists='replace') 

