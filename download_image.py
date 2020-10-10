#!/usr/bin/env python
# coding: utf-8

### Import Packages
import requests
import re
import os
import pandas as pd
import numpy as np
import sqlite3
import datetime
import cv2
import sys
from sqlalchemy import create_engine


##########################Define functions#############################

## Download urls function
def down_urls(html):
    url_pics = re.findall('<img alt=".*?" src="(.*?)" height="', str(html.text), re.S)
    return url_pics

## Download image function
def down_pics(url_list,addr):
    i=0
    name_list = []
    local_list = []
    down_time_list = []
    width_list = []
    height_list = []
    color_list = []
    for each in url_list:
        print('Downloading the' + str(i) + '，image address：' + str(each))
        try:
            pic = requests.get(each, timeout=10)
        except requests.exceptions.ConnectionError:
            print('Error！This image cannot be downloaded')
            continue
            
        # create local path
        dir = addr  + str(i) + '.jpg'
        
        # record image name, local location, download time
        name_list.append(i)
        local_list.append(dir)
        down_time_list.append(datetime.datetime.now())
        with open(dir, 'wb') as file:
            file.write(pic.content)
            
        # read the image width, height and channel
        img = cv2.imread(dir)
        sp = img.shape
        height_list.append(sp[0]) #height(rows) of image
        width_list.append(sp[1]) #width(colums) of image
        color_list.append(sp[2]) #the pixels value is made up of three primary colors
        
        i+=1
        
    ## Save these images structured in a tabular format
    df1 = pd.DataFrame({'Image_name':name_list,'Image_url':url_list,                       'Width':width_list,'Height':height_list,'Color_channels':color_list,            'Download_datetime':down_time_list,'Image_location':local_list})
    
    return df1
    
            
## SQL select function
def select(query):
    conn = sqlite3.connect('foo.db')
    cursor = conn.cursor()
    cursor.execute(query)
    values = cursor.fetchall()
    cursor.close()
    conn.close()
    return values


##########Find images and download them into local address, as well as save their info and load into db###########

###### 1. Download data and load them into sqlite db ###
# Eg. 100+ images from Amazon 100 Best sellers in women clothings page
url1 = 'https://www.amazon.com/Best-Sellers-Womens-Clothing/zgbs/fashion/1040660/ref=zg_bs_nav_2_7147440011'
url2 = 'https://www.amazon.com/Best-Sellers-Womens-Clothing/zgbs/fashion/1040660/ref=zg_bs_pg_2?_encoding=UTF8&pg=2'

result1 = requests.get(url1)
url_list = down_urls(result1)
result2 = requests.get(url2)
url_list.extend(down_urls(result2))

## put urls download in a dataframe
df_1 = pd.DataFrame({'urls':url_list})

# load dataframe into sql database
engine = create_engine('sqlite:///foo.db')
print(df_1)
df_1.to_sql('image_urls', engine, if_exists='replace')
print('Sucessfully find 100+ images and put them into db!')


###### 2&3. download images into local address and save them in table into db
# fetech urls in the first table
urls_list = [url[0] for url in select('select urls from image_urls')]
# set local adress
address = sys.argv[1]
df_2 = down_pics(urls_list,address)

# load dataframe into sql database
engine = create_engine('sqlite:///foo.db')
df_2.to_sql('image_info', engine, if_exists='replace')
print('Sucessfully download 100+ images and save their info into db!')

# ## Table 1: 
# print(df_1)

# ## select from sqlite db
# select('select * from image_urls')


# In[9]:


# ## Table2:
# print(df_2)

# ## select from sqlite db
# select('select * from image_info')

