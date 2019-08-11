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
    
df
