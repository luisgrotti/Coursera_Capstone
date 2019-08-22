import pandas as pd
from geopy import Nominatim
from geopy import distance
import requests
import folium
import numpy as np

#http://geosampa.prefeitura.sp.gov.br/PaginasPublicas/_SBC.aspx#

sp_districts = pd.read_csv(r'C:\Users\luisg\Downloads\mygeodata\LL_WGS84_KMZ_distrito.csv')

sp_districts.drop(['gid', 'Name', 'description', 'Field_1'], axis=1, inplace=True)
sp_districts.columns = ['Longitude', 'Latitude', 'District']
sp_districts = sp_districts[['District', 'Latitude', 'Longitude']]

distances = []
for i_1, row_1 in sp_districts.iterrows():
    dist_1 = 1000
    loc1 = (sp_districts['Latitude'][i_1], sp_districts['Longitude'][i_1])
    for i_2, row_2 in sp_districts.iterrows():
        loc2 = (sp_districts['Latitude'][i_2], sp_districts['Longitude'][i_2])
        dist_2 = distance.distance( loc1, loc2).km
        if dist_2 < dist_1 and dist_2 != 0:
            dist_1 = dist_2
    distances.append(dist_1)

distances = pd.DataFrame(distances)
distances.columns = ['aaaa']
mean = distances['aaaa'].mean()

#it means min distance to other district is about 3km
client_id = 'IG0WM4KPS4BQG2SWJU0RB0ISV1OUVFHESE5MGEWCIVBHWWYP' # your Foursquare ID
client_secret = 'EPFTFBU0VTX0YEEAZA0KOYZFYJRLOHKFGEIUVNT3D5YRFW2F' # your Foursquare Secret
version = '20180605' # Foursquare API version 20180605



def getTrendingVenues(names, latitudes, longitudes, radius=3000):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
        print(lat)
        print(lng)
        
        # set limit
        LIMIT = 50
        # 'https://api.foursquare.com/v2/venues/trending?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&intent{}&radius={}&limit={}'.format(
            client_id, 
            client_secret, 
            version, 
            lat, 
            lng,
            'global',
            radius, 
            LIMIT)
            
        # make the GET request
#        results = requests.get(url).json()
        results = requests.get(url).json()["response"]['groups'][0]['items']
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['id'],
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])
    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue ID',
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)
    
sp1_districts = sp_districts[48:49]

sp_venues = getTrendingVenues(names=sp1_districts['District'], latitudes=sp1_districts['Latitude'], longitudes=sp1_districts['Longitude'])
sp_venues_1 = sp_venues[0:1]


def getVenueDetails(venue_ids):
    
    details_list=[]
    for venue_id in venue_ids:
        print(type(venue_id))
        print(venue_id)
        
#        # create the API request URL
#        url = 'https://api.foursquare.com/v2/venues/VENUE_ID/hours?&client_id={}&client_secret={}&v={}&VENUE_ID={}'.format(
#            client_id, 
#            client_secret, 
#            version, 
#            venue_id)
#        print(url)   
        
        
        url = 'https://api.foursquare.com/v2/venues/4b716f26f964a52078462de3/hours'
        
        
        params = dict(client_id=client_id,
                      client_secret=client_secret,
                      v=version)
#                      VENUE_ID='4f5dd48ae4b0d8f7b8293a22')

        resp = requests.get(url=url, params = params).json()
#        data = json.loads(resp.text)
        print(resp)
        
        resp_teste = resp
        
        resp['response']['popular']['timeframes']
        resp_df = pd.DataFrame.from_dict(resp['response']['popular']['timeframes'])
        resp_df.drop(['includesToday', 'segments'], axis=1, inplace=True)
        resp_df['open'] = resp_df['open'].apply(pd.Series)
        resp_df_1 = pd.concat([resp_df.drop(['open'], axis=1), resp_df['open'].apply(pd.Series)], axis=1)
        resp_df_2 = resp_df_1['days'].apply(pd.Series).stack().reset_index(level=0, drop=True).to_frame('days')
        resp_df_2  = pd.DataFrame({'days':np.concatenate(resp_df_1['days'].values), 
                                   'start':np.repeat(resp_df_1['start'].values, resp_df_1['days'].str.len()),
                                   'end':np.repeat(resp_df_1['end'].values, resp_df_1['days'].str.len())})
        # make the GET request
#        results = requests.get(url).json()["response"]['groups'][0]['items']
#        results = requests.get(url).json()
#        print(results)
#        # return only relevant information for each nearby venue
#        details_list.append([(
#            venue_id, 
#            v['venue']['hours'], 
#            v['venue']['popular'], 
#            v['venue']['days'] ) for v in results])
##            v['venue']['categories'][0]['name']
#    nearby_venues = pd.DataFrame([item for detail_list in details_list for item in detail_list])
#    nearby_venues.columns = ['Venue ID', 
#                  'popular', 
#                  'days']
#    
    return(nearby_venues)


sp_venues_details = getVenueDetails(venue_ids=sp_venues_1['Venue ID'])

sp_venues_1['Venue ID']












#-------MAP

address = 'São Paulo, SP'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Manhattan are {}, {}.'.format(latitude, longitude))

# create map of Manhattan using latitude and longitude values
map_manhattan = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(sp1_districts['Latitude'], sp1_districts['Longitude'], sp1_districts['District']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_manhattan)  

for lat, lng, label in zip(sp_venues['Venue Latitude'], sp_venues['Venue Longitude'], sp_venues['Venue']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=3,
        popup=label,
        color='red',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_manhattan)  

    
map_manhattan.save('aaa.html')

#-------MAP