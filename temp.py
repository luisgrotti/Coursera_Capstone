    #TROCAR TODOS OS NOMES NEIGHBOURHOOOD POR NEIGHBORHOOD
    # importing necessaru dependencies
    import pandas as pd
    
    # getting table from Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
    df = pd.read_html(url, header=None)
    df = df[0]
    
    # let's check how much Borough is not assinged
    df['Borough'].value_counts()
    
    # We see that in 77 cases Borough is not assigned. Let's take those row out of our dataset
    df.drop(df[df['Borough'] == 'Not assigned'].index, axis=0, inplace=True)
    df.reset_index(drop=True,inplace=True)
    
    # Now let's group all Neighborhoods that has same Postcode in same row, separated by comma, let's how much Postcodes has multiple registers
    mult_postcode = df.groupby(['Postcode']).count()
    mult_postcode['Neighbourhood'].value_counts()
    
    # Now lets aggregate the mulpiple lines by postcode
    df = df.groupby(['Postcode', 'Borough'], as_index=False).agg(', '.join)
    
    #Now just to check we count again our dataframe to check if any post code remias with multiple neighbourhood
    mult_postcode = df.groupby(['Postcode']).count()
    mult_postcode['Neighbourhood'].value_counts()
    
    # now let's see if theres ani Borough containeng the label not assigned
    df[df['Neighbourhood'].str.contains('Not assigned') == True]
    
    # so row 85 is the only one we should assig Queens Park to neighbourhood
    df.iloc[85]['Neighbourhood'] = df.iloc[85]['Borough']
    
    # now that our dataset was cleaned lets see its shape
    df.shape
    
    
    
    
    
    
    
    # in order to get the latitude and longitude data for each postal code let's loop df['Pstocode'] 
    # and use the geocoder python packeage to get the info to do so lets import geocoder
    #!pip install geocoder --user
    
    
    #first lets create two columns to hold latitude and logintude in our dataframe
    #df['Latitude'].astype('float') = 0
    #df['Longitude'] = 0
    df['Latitude'] = pd.Series(dtype='float')
    df['Longitude'] = pd.Series(dtype='float')
    #now lets get a csv file with latitude longitude for each postcode
    codes = pd.read_csv('http://cocl.us/Geospatial_data',  float_precision = '%.7f')
    codes
    # lets check if we can transform Postal Code in index 
    #codes[codes['Postal Code'].value_counts() > 1 == True].value_counts()
    #aaa = codes.groupby('Postal Code').count()
    #now lets loop our dataframe to add each latitude and longitude coordinates
    codes[codes.duplicated() == True]
    codes.set_index('Postal Code', inplace=True)
    df.dtypes
    for index, row in df.iterrows():
        #print(index, row)
        df.at[index,'Latitude'] = codes.loc[row[0],'Latitude']
        df.at[index,'Longitude'] = codes.loc[row[0],'Longitude']
        #df.at(index, row[4]) = 5
        #
        #row['Longitude'] = codes.loc[row[0],'Longitude']
        
    #----------------------------------
        
        
        
    df1 = df[:]
    df = df1[:]
    #in order to work just with locations in toronto, lets drop all lines outside toronto
    df.drop(df[df['Borough'].str.contains('Toronto')==False].index, inplace=True )
    df.reset_index(drop=True, inplace=True)
    
    
    # not lets see these where are the boroughs in the map, but first we need toronto latitude
    # for this task we are going to use geopy library
    from geopy.geocoders import Nominatim 
    
    
    address = 'Toronto, CA'
    
    geolocator = Nominatim(user_agent="ca_explorer")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    print('The geograpical coordinate of Toronto CA are {}, {}.'.format(latitude, longitude))
    
    
    #now we are ready to use folium to plot the boroughs
    #!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
    
    import folium
    import json
    import requests # library to handle requests
    
    
    # create map of New York using latitude and longitude values
    map_newyork = folium.Map(location=[latitude, longitude], zoom_start=10)
    
    # add markers to map
    for lat, lng, borough, neighborhood in zip(df['Latitude'], df['Longitude'], df['Borough'], df['Neighbourhood']):
        label = '{}, {}'.format(neighborhood, borough)
        label = folium.Popup(label, parse_html=True)
        folium.CircleMarker(
            [lat, lng],
            radius=5,
            popup=label,
            color='blue',
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.7,
            parse_html=False).add_to(map_newyork)  
        
    map_newyork.save("mymap.html")
    
    
    #now lets use foursquare to get interesting places around each neighbourhood, so we can cluster them
    #first lets assign secret data
    
    CLIENT_ID = 'IG0WM4KPS4BQG2SWJU0RB0ISV1OUVFHESE5MGEWCIVBHWWYP' # your Foursquare ID
    CLIENT_SECRET = 'EPFTFBU0VTX0YEEAZA0KOYZFYJRLOHKFGEIUVNT3D5YRFW2F' # your Foursquare Secret
    VERSION = '20180605' # Foursquare API version
    
    def getNearbyVenues(names, latitudes, longitudes, radius=500):
        
        venues_list=[]
        for name, lat, lng in zip(names, latitudes, longitudes):
            print(name)
            
            # set limit
            LIMIT = 100
            
            # create the API request URL
            url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
                CLIENT_ID, 
                CLIENT_SECRET, 
                VERSION, 
                lat, 
                lng, 
                radius, 
                LIMIT)
                
            # make the GET request
            results = requests.get(url).json()["response"]['groups'][0]['items']
            
            # return only relevant information for each nearby venue
            venues_list.append([(
                name, 
                lat, 
                lng, 
                v['venue']['name'], 
                v['venue']['location']['lat'], 
                v['venue']['location']['lng'],  
                v['venue']['categories'][0]['name']) for v in results])
    
        nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
        nearby_venues.columns = ['Neighborhood', 
                      'Neighborhood Latitude', 
                      'Neighborhood Longitude', 
                      'Venue', 
                      'Venue Latitude', 
                      'Venue Longitude', 
                      'Venue Category']
        
        return(nearby_venues)
    
    toronto_venues = getNearbyVenues(names=df['Neighbourhood'], latitudes=df['Latitude'], longitudes=df['Longitude'])
    
    
    
    #LETS SEE THE SIZE OF THIS SHIT
    print(toronto_venues.shape)
    
    
    #see venues per neighbourhood
    toronto_venues.groupby('Neighborhood').count()
    #unique categories
    print('There are {} uniques categories.'.format(len(toronto_venues['Venue Category'].unique())))
    
    #now blablabla analysis
    # one hot encoding
    toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")
    
    # add neighborhood column back to dataframe
    toronto_onehot['Neighborhood_'] = toronto_venues['Neighborhood'] 
    
    # move neighborhood column to the first column
    fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
    toronto_onehot = toronto_onehot[fixed_columns]
    
    toronto_onehot.head()
    
    
    #### Next, let's group rows by neighborhood and by taking the mean of the frequency of occurrence of each category
    toronto_grouped = toronto_onehot.groupby('Neighborhood_').mean().reset_index()
    
    import numpy as np
    
    # confirm new size
    toronto_grouped.shape
    
    
    #### Let's print each neighborhood along with the top 5 most common venues
    num_top_venues = 5
    
    for hood in toronto_grouped['Neighborhood_']:
        print("----"+hood+"----")
        temp = toronto_grouped[toronto_grouped['Neighborhood_'] == hood].T.reset_index()
        temp.columns = ['venue','freq']
        temp = temp.iloc[1:]
        temp['freq'] = temp['freq'].astype(float)
        temp = temp.round({'freq': 2})
        print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
        print('\n')
        
    #### Let's put that into a *pandas* dataframe - First, let's write a function to sort the venues in descending order.
    def return_most_common_venues(row, num_top_venues):
        row_categories = row.iloc[1:]
        row_categories_sorted = row_categories.sort_values(ascending=False)
        
        return row_categories_sorted.index.values[0:num_top_venues]
    
    #Now let's create the new dataframe and display the top 10 venues for each neighborhood.
    num_top_venues = 10
    
    indicators = ['st', 'nd', 'rd']
    
    # create columns according to number of top venues
    columns = ['Neighborhood_']
    for ind in np.arange(num_top_venues):
        try:
            columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
        except:
            columns.append('{}th Most Common Venue'.format(ind+1))
    
    # create a new dataframe
    neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
    neighborhoods_venues_sorted['Neighborhood_'] = toronto_grouped['Neighborhood_']
    
    for ind in np.arange(toronto_grouped.shape[0]):
        neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)
    
    neighborhoods_venues_sorted.head()
    
    # now we have everything rwady lets run k menas
    # import k-means from clustering stage
    from sklearn.cluster import KMeans
    # set number of clusters
    kclusters = 5
    
    toronto_grouped_clustering = toronto_grouped.drop('Neighborhood_', 1)
    
    # run k-means clustering
    kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)
    
    # check cluster labels generated for each row in the dataframe
    kmeans.labels_ 
    
    
    #Let's create a new dataframe that includes the cluster as well as the top 10 venues for each neighborhood.
    
    # add clustering labels
    neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)
    
    df_merged = df
    
    # merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
    toronto_merged = df_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood_'), on='Neighbourhood')
    
    df_merged.head() # check the last columns!
    
    
    
    
    # create map
    # Matplotlib and associated plotting modules
    import matplotlib.cm as cm
    import matplotlib.colors as colors
    
    map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)
    
    # set color scheme for the clusters
    x = np.arange(kclusters)
    ys = [i + x + (i*x)**2 for i in range(kclusters)]
    colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
    rainbow = [colors.rgb2hex(i) for i in colors_array]
    
    # add markers to the map
    markers_colors = []
    for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'], toronto_merged['Neighbourhood'], toronto_merged['Cluster Labels']):
        label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
        folium.CircleMarker(
            [lat, lon],
            radius=5,
            popup=label,
            color=rainbow[cluster-1],
            fill=True,
            fill_color=rainbow[cluster-1],
            fill_opacity=0.7).add_to(map_clusters)
           
    
    map_clusters.save("mymap_cluster.html")
    
    
    
    #Now, you can examine each cluster and determine the discriminating venue categories that distinguish each cluster. Based on the defining categories, you can then assign a name to each cluster. I will leave this exercise to you.
    
    toronto_merged.loc[toronto_merged['Cluster Labels'] == 0, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]
    toronto_merged.loc[toronto_merged['Cluster Labels'] == 1, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]
    toronto_merged.loc[toronto_merged['Cluster Labels'] == 2, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]
    toronto_merged.loc[toronto_merged['Cluster Labels'] == 3, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]
    toronto_merged.loc[toronto_merged['Cluster Labels'] == 4, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]