# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 17:24:33 2019

@author: luisg
"""


## Agênia de turismo criou uma lista de categorias com as categorias do Foursquare para classificar as cidades pelo mundo quanto as suas atrações.
## Lista de cidades mais turisticas do mundo para fazer a pesquisa por locais

## para a análise precisamos de cidades com boa oferta de locomoção
## verificar para as cidades que estão com venues longe do centro se possui boa rede de transporte
## apenas cidades com aeroporto
## para aqueles com mais venues perto do centor verificar se possuem metro onibos taxi
## para aqueles onde a maioria das venus está longe do centro verificar se possue transporte ou alugues de carro


# importing relevant libraries
import pandas as pd
#pip install pycountry-convert
import pycountry_convert as pc
import seaborn as sns
import numpy as np
#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't installed geopy in your enviromment
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
import folium 
import json # library to handle JSON files
import requests # library to handle requests


# reading the list of categories provided by Tourism Company
tc_categories = pd.read_csv(r'C:\Users\luisg\Documents\GitHub\Coursera_Capstone\tc_venues_categories.csv')
tc_categories.head()

# Let's scrap Wikipedia to get the list of top 100 cities ranked by the number of international visitors
top_cities = pd.read_html('https://en.wikipedia.org/wiki/List_of_cities_by_international_visitors')
top_cities = top_cities[0]
top_cities.head()

# As you can see, there's two different rankings, we are not interested in Mastercard's Rank, let's drop cities which are listed just for Mastercard
top_cities = top_cities[top_cities['RankEuromonitor'].notnull()]
top_cities.drop(['RankMastercard', 'Income(billions $)Mastercard', 'Arrivals 2016Mastercard'], axis=1, inplace=True)
top_cities.columns = ['Rank', 'City', 'Country', 'Arrivals_2017', 'Arrivals_growth']

# To proceed with analysis, we need to find continet for each city in top_cities.
top_cities['Continent'] = ''

for i, row in top_cities.iterrows():
    country_code = pc.country_name_to_country_alpha2(row['Country'], cn_name_format="default") 
    continent_name  = pc.country_alpha2_to_continent_code(country_code)
    top_cities.loc[i, 'Country'] = country_code 
    top_cities.loc[i, 'Continent'] = continent_name

# Let's check what we got
top_cities['Continent'].value_counts()

# It seems pycountry assumes that North America (NA) and South America (SA) are different continents (!). Let's put them together under AM ('America')
top_cities['Continent'].replace('NA', 'AM', inplace=True)
top_cities['Continent'].replace('SA', 'AM', inplace=True)

# Now everyone is in its place
top_cities['Continent'].value_counts()

# Our demand is to cluster just the top 5 cities in each continent by considering their growth in arruvals. Let's check datatypes
top_cities.dtypes

# Let's cast Arrivals_growth into float
top_cities['Arrivals_growth'] = top_cities['Arrivals_growth'].replace('%','', regex=True)
top_cities['Arrivals_growth'] = top_cities['Arrivals_growth'].replace(',','.', regex=True)
top_cities['Arrivals_growth'] = top_cities['Arrivals_growth'].replace('−','-', regex=True).astype(float)
top_cities.dtypes

# Let's visualize how Arrivals Growth are spread using continent to group it
# We'll use seaborn 
sns.boxplot(x=top_cities['Continent'], y=top_cities['Arrivals_growth'])

# As we can see there's a lot of outliers in Asia, we could be good to take it off and work with 'normal' data (search for a reason)
top_cities.sort_values(by=['Arrivals_growth'], ascending=True, inplace=True)
arr_grw_asia = top_cities[top_cities['Continent'] == 'AS']['Arrivals_growth'].to_frame()
arr_grw_asia.sort_values(by='Arrivals_growth', inplace=True)


p_25, p_75 = np.percentile(arr_grw_asia , [25, 75])
iqr = p_75 - p_25

upper_bound = p_75 + 1.5 * iqr
lower_bound  = p_25 - 1.5 * iqr

top_cities = top_cities.drop(top_cities[(top_cities['Continent'] == 'AS') & (top_cities['Arrivals_growth'] > upper_bound)].index)
top_cities = top_cities.drop(top_cities[(top_cities['Continent'] == 'AS') & (top_cities['Arrivals_growth'] < lower_bound)].index)

# Let's see how it look now.
sns.boxplot(x=top_cities['Continent'], y=top_cities['Arrivals_growth'])
avg_arr_grw = []

# Now let's calculate the average Arrivals_growth for each continent and exclude cities which have Arrivals_growth less than its continent average
top_cities['avg_arr_growth_cont'] = top_cities.groupby('Continent')['Arrivals_growth'].transform('mean')
top_cities = top_cities.drop(top_cities[(top_cities['Arrivals_growth'] < top_cities['avg_arr_growth_cont']) & (top_cities['Continent'] != 'OC') & (top_cities['Continent'] != 'AF')].index)

# Now lets see in the map the cities

geolocator = Nominatim(user_agent="ca_explorer")
location = geolocator.geocode(top_cities['City'] + ', ' + top_cities['Country'])
top_cities['lat'] = location.latitude
top_cities['long'] = location.longitude
print('The geograpical coordinate of Toronto CA are {}, {}.'.format(toronto_latitude, toronto_longitude))


geolocator = Nominatim(user_agent="ca_explorer")
top_cities['lat'] = 0
top_cities['long'] = 0
top_cities1 = top_cities[0:1]
for i, row in top_cities.iterrows():
    location = geolocator.geocode(row['City'] + ', ' + row['Country'])
    print(location)
    print(location.latitude)
    print(location.longitude)
    top_cities.loc[i, 'Lat'] = location.latitude
    top_cities.loc[i, 'Long'] = location.longitude

# create map of Toronto using its latitude and longitude
world_map = folium.Map()
    
# add markers to map
for lat, lng, city in zip(top_cities['Lat'], 
                                           top_cities['Long'], 
                                           top_cities['City']):
    label = '{}'.format(city)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(world_map)  
        
world_map.save('world_map.html')

# Now, let's get the venues for each city

# setting API credentials
client_id = 'IG0WM4KPS4BQG2SWJU0RB0ISV1OUVFHESE5MGEWCIVBHWWYP' # your Foursquare ID
client_secret = 'EPFTFBU0VTX0YEEAZA0KOYZFYJRLOHKFGEIUVNT3D5YRFW2F' # your Foursquare Secret
version = '20180605' # Foursquare API version

# creating a function to get from Foursquare up to 100 nearby venues for a given coordinate
def getNearbyVenues(cities, countries, categories, limit=100):
    
    venues_list=[]
    
    for city, country in zip(cities, countries):
        print('Searching in', city + ' ,' + country)
        
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/search?&client_id={}&client_secret={}&v={}&near={}&categoryId={}&limit={}'.format(
            client_id, 
            client_secret, 
            version, 
            city + ' ,' + country, 
            #'global', 
            categories, 
            limit)
        
        # make the GET request
        results = requests.get(url).json()["response"]['venues']
        # return only relevant information for each nearby venue
        
        #for resp in results:
        #    venues_list.append([city, country, resp['name'], resp['categories'][0]['id'], resp['categories'][0]['name']])
            #resp['categories'][0]['name']])
            
        venues_list.append([(
            city, 
            country, 
            v['name'],  
            v['categories'][0]['id'],
            v['categories'][0]['name']) for v in results])
    
    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['City', 'Country', 'Venue', 'Category ID', 'Category']
    
    return(nearby_venues)

top_cities_venues = getNearbyVenues(cities=top_cities['City'], 
                                countries=top_cities['Country'], 
                                categories=','.join(tc_categories['cat_id'].astype(str)))

top_cities_venues.head()


