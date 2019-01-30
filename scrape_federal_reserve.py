#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 18:50:12 2019

@author: grant
"""

import requests
import pandas as pd
import numpy as np
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}

def get_codes(test):
    
        country_dict = {'Australia':'al',
                'Austria':'au',
                'Belgium':'be',
                'Brazil':'bz',
                'Canada':'ca',
                'China, P.R.':'ch',
                'Denmark':'dn',
                'EMU member countries':'eu',
                'European Union':'ec',
                'Finland':'fn',
                'France':'fr',
                'Germany':'ge',
                'Greece':'gr',
                'Hong Kong':'hk',
                'India':'in',
                'Ireland':'ir',
                'Italy':'it',
                'Japan':'ja',
                'Malaysia':'ma',
                'Mexico':'mx',
                'Netherlands':'ne',
                'New Zealand':'nz',
                'Norway':'no',
                'Portugual':'po',
                'Singapore':'si',
                'South Africa':'sf',
                'South Korea':'ko',
                'Spain':'sp',
                'Sri Lanka':'sl',
                'Sweden':'sd',
                'Switzerland':'sz',
                'Taiwan':'ta',
                'Thailand':'th',
                'United Kingdom':'uk',
                'Venezuela':'ve'}
    

        
        s = pd.Series(country_dict)
        df_code = pd.DataFrame({'Country':s.index, 'code':s.values})
        if test:
            df_code = df_code.sample(n=1)
        return(df_code)

def get_structure(url_l, code_frame):
    lis = []
    
    try:
        
        for r in url_l:
        
            if r != 'https://www.federalreserve.gov/releases/h10/hist/default.htm':
                df_exchange = pd.read_html(r,header = 0)[2]
                df_exchange = df_exchange.drop([0, 0])
                df_exchange['Country'] = df_exchange['Country or region'].str.replace(r"\(.*\)","")
                df_exchange['Country'] = df_exchange['Country'].str.rstrip() 
                df_exchange['Contains data'] = df_exchange['Country or region'].str.contains('no data', na=False)
                contains_data = [not x for x in df_exchange['Contains data']]
                df_exchange = df_exchange[contains_data]
                df_exchange = pd.merge(df_exchange,code_frame, left_on = 'Country', right_on = 'Country')
                df_exchange['year'] = url_l[r]
                lis.append(df_exchange)
            else:
                df_exchange = pd.read_html(r,header = 0)[0]
                df_exchange = df_exchange.drop([0, 0])
                df_exchange['Country'] = df_exchange['Country'].str.replace(r"\(.*\)","")
                df_exchange['Country'] = df_exchange['Country'].str.rstrip() 
                df_exchange['Contains data'] = df_exchange['Country'].str.contains('no data', na=False)
                contains_data = [not x for x in df_exchange['Contains data']]
                df_exchange = df_exchange[contains_data]
                df_exchange = pd.merge(df_exchange,code_frame, left_on = 'Country', right_on = 'Country')
                df_exchange['year'] = url_l[r]
                lis.append(df_exchange)
            
        return(lis)
    
    except:
        print('Cant get detail for'+ str(r))
        pass
    
def exchange_list(df_list, base_url):
    exchange_data = []
    url_ext = base_url
    for df in df_list:
        
        try:
     
            for x,m,c,y in zip(df['code'],df['Monetary unit'],df['Country'],df['year']):
                url_ext = base_url.replace('YYYY',str(y)) # add the date to the end of url
                url_ext = url_ext.replace('CC', str(x))       
                r = requests.get(url_ext, allow_redirects=True, stream=True, headers=headers)
                if r.status_code == requests.codes.ok:
                    df_ex = pd.read_html(url_ext, header = 0)[0]
                    df_ex['Monetary Unit'] = str(m)
                    df_ex['Country'] = str(c)
                    #print(df_ex.head())
                    exchange_data.append(df_ex)
                
                else:
                    print('couldnt get data for' +str(x)+' '+str(y))
                    
        except:
            print('Cant get rates for'+' '+str(c)+' '+str(url_ext))
            continue
                
    exchange = pd.concat(exchange_data, axis=0, sort=False, ignore_index=True)
    exchange = exchange.dropna(axis=0)
    
    return(exchange)
    
def get_rates(test):

    url_dict= {'https://www.federalreserve.gov/releases/h10/hist/default1989.htm':'89', 
               'https://www.federalreserve.gov/releases/h10/hist/default1999.htm':'96', 
               'https://www.federalreserve.gov/releases/h10/hist/default.htm':'00'}

    url = 'https://www.federalreserve.gov/releases/h10/hist/datYYYY_CC.htm' #base url
    
    if test:
        df_detail = get_codes(test=True)
        #print(df_detail)
    else:
        df_detail = get_codes(test=False)
        #print(df_detail)
        
    df = get_structure(url_dict, df_detail)
    federal_reserve = exchange_list(df, url)
    federal_reserve.replace('ND', np.nan, inplace=True)
    federal_reserve.replace('NC', np.nan, inplace=True)
    federal_reserve['Date'] = pd.to_datetime(federal_reserve['Date'])
    federal_reserve['Rate'] = federal_reserve['Rate'].astype('float64')
    federal_reserve['Monetary Unit'] = federal_reserve['Monetary Unit'].astype('object')
    federal_reserve['Country'] = federal_reserve['Country'].astype('object')
    federal_reserve['Monetary Unit'] = federal_reserve['Monetary Unit'].astype('object')
    #add the columns column later for doing analysis and creating the unpivoted column headings
    #federal_reserve['Columns'] = federal_reserve['Country']+'-'+federal_reserve['Monetary Unit']
    
    return(federal_reserve)
    

rates = get_rates(test=True)
print(rates.head())