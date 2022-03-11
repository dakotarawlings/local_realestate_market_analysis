
"""
Scraper for housing information on trulia using beautiful soup
The main callable function is defined at the bottom:
    
web_scraoer(trulia_link: str, number_pages: int)-> df


"""


from bs4 import BeautifulSoup
import time
import numpy as np
import pandas as pd
import regex as re
import requests



#HTTP header for requests:
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Chrome/61.0.3163.100 Safari/537.36'
}

#list of browser codes used in the user agent of the http requests. 
#the user agents are alternated to avoid coming across as a bot
user_agent_list=['Chrome/61.0.3163.100 Safari/537.36','AppleWebKit/537.36 (KHTML, like Gecko)','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36']


# Get list of links for each house listing
def get_house_links(base_link, num_pages): 
    
    #takes in an http link for a search on trulia.com search 
    #and number of pages and retrieves the 
    
    global req_headers
    link_list=[]
    
    #start a request session
    with requests.Session() as s:
        
        #loop through all pages
        for i in range(1,num_pages+1):
            
            #add desired page number to the base http link
            link=base_link+str(i)+"_p/"
            
            #make the http request
            with requests.Session() as s:
                data=s.get(link,headers=req_headers)
            
            #use beautiful soup to transform the output from the request to a soup object that can be easily analyzed
            soup=BeautifulSoup(data.content,'html.parser')
            
            #find all of the property card tags in the HTML doc
            house_link=soup.find_all("a",class_=re.compile('PropertyCard'))

            #extract the link string from the property card and add the rest of the HTTP request
            for n in [item['href'] for item in house_link]:
                link_list=link_list+["https://www.trulia.com/"+n]

            #rendomly vary the time and the header in between every 4 requests  to seem more human-like
            if i%4==0:
                r=np.random.randint(0,3)
                user_agent=user_agent_list[r]
                req_headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.8',
                    'upgrade-insecure-requests': '1',
                    'user-agent': user_agent
                    }
                
                
                time.sleep(np.random.randint(60,180))
            
            #randomly vary the time in between each request to seem more human
            time.sleep(np.random.randint(20,30))
    return link_list



#Retrieve data from a list of trulia links and add to data frame    
def extract_link_data(link_list): 
#Takes in list of links for trulia house listings and trurns dataframe of data for all links
    global req_headers
    
    price_list=[]
    address_list=[]
    zip_list=[]
    beds_list=[]
    baths_list=[]
    building_sqft_list=[]
    year_built_list=[]
    lot_area_list=[]
    
    #start a requests session
    with requests.Session() as s:
        
        #loop through each link in the list of links for house listings
        for i in range(len(link_list)):
            link=link_list[i]
            
            #get HTML doc from house listing
            data=s.get(link,headers=req_headers)
            soup=BeautifulSoup(data.content,'html.parser')
            
            #Uncomment to save HTML data to directory to save progress in case program stops 
            #do to a "captcha" bot on the site
            '''
            with open("C:/Users/dakot/Desktop/DataScience/Project Scrap work/trulia_project/raw_page_html/"+str(i)+".html", "w") as f:
                f.write(str(data.content))
            '''
            
            #use our extraction functions (defined below) to extract information from links and add to lists
            price_list.append(get_price(soup))
            address_list.append(get_address(soup))
            zip_list.append(get_zip(soup))
            beds_list.append(get_beds(soup))
            baths_list.append(get_baths(soup))
            year_built_list.append(get_year_built(soup))
    
            #There are two different spots on the site where building and lot area are listed so I try both
            building_area=get_building_area(soup)
            if pd.isnull(building_area):
                building_area=get_living_area(soup)
            
            lot_area=get_lot_area(soup)        
            if pd.isnull(lot_area):
                lot_area=get_lot_area_alt(soup)
                
            building_sqft_list.append(building_area)
    
            lot_area_list.append(lot_area)
                 
            #Randomly vary the time and header every 4 requests to seem less bot-like
            if i%4==0:
                r=np.random.randint(0,3)
                user_agent=user_agent_list[r]
                req_headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.8',
                    'upgrade-insecure-requests': '1',
                    'user-agent': user_agent
                    }
                
                
                time.sleep(np.random.randint(60,180))
            
            #randomly vary the time in between requests to seem less robot-like
            time.sleep(np.random.randint(20,30))
            
            print(i)
    
    #make a dataframe with all of the data
    dataframe=pd.DataFrame({'price':price_list,'address':address_list,'zip':zip_list,'num_bedrooms':beds_list,'num_baths':baths_list,'building_sqft':building_sqft_list,'year_built':year_built_list,'lot_area':lot_area_list})
    return dataframe


# The following "get" functions are used in the function above to parse the HTML data
#Each function takes in a soup object created using beautiful soup and return a value

def get_price(soup):
    # Takes in soup object and returns price as int
    try:
        price=float([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-details-price-detail'][0].replace('$','').replace(',',''))    
        return price
    except:
        return np.nan

def get_address(soup):
    #Takes in soup object and returns address as a string
    try:
        address=str([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-details-summary-address'][0])    
        return address
    except:
        return 'None'
def get_zip(soup):
    #Takes in soup object and returns zipcode as a string
    try:
        zip=str([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-details-summary-city-state'][0])    
        return (re.sub('\D','',zip))
    except:
        return 'None'
    
def get_beds(soup):
    #Takes in soup object and returns the number of bedrooms as an int
    try:
        num_beds=float(([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-summary-size-bedrooms'][0]).lower().replace('beds',''))  
        return num_beds
    except:
        return np.nan

def get_baths(soup):
    #Takes in soup object and returns the number of bathrooms as an int
    try:
        num_baths=float(([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-summary-size-bathrooms'][0]).lower().replace('baths',''))
        return num_baths
    except:
        return np.nan
    
def get_year_built(soup):
    #Takes in soup object and returns the year built as an int
    try:
        table_text=[item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='structured-amenities-table-category']
        for item in table_text:
            item=item.lower()
        
            if 'year built' in item:
                i=item.index('year built')
                year_built=item[i:i+100]
                possible_years=list(range(1900,2022))
                possible_years=[str(year) for year in possible_years]
                try:
                    year_built=int([year for year in possible_years if year in year_built][0])
                except:
                    year_built=np.nan
        return year_built
    except:
        return np.nan
    
def get_lot_area(soup):
    #Takes in soup object and returns lot area in acres as an int
    try:
        table_text=[item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='structured-amenities-table-category']
        for item in table_text:  
            item=item.lower()              
                
            if 'lot area' in item:
                if 'feet' in item:
                    lot_sqft=item.replace('feet','').replace('square','').replace('area','').replace('lot','').replace('information','').replace(':','')
                    lot_area=float(lot_sqft)/43560
                if 'acres' in item:
                    lot_area=item.replace('acres','').replace('area','').replace('lot','').replace('information','').replace(':','')
                    lot_area=float(lot_area)

        return lot_area
    except:
        return np.nan   
    
def get_lot_area_alt(soup):
    #Takes in soup object and returns the lot size in acres as an int (alternative to lot_area)
    try:
        lot_size=([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-summary-size-lotsize'][0].replace('(','').replace(')','').replace('on','').replace('acre','').replace('s',''))    
        return float(lot_size)
    #*43560
    except:
        return np.nan


def get_building_area(soup):
    #Takes in soup object and returns the building area in sq feet as an int
    try:
        table_text=[item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='structured-amenities-table-category']
        for item in table_text:
            item=item.lower()
            if 'building area' in item:
                house_sqft=item.replace('building','').replace('area','').replace(':','').replace('square','').replace('feet','')
                house_sqft=float(house_sqft)
        return house_sqft
    except:
        return np.nan
        
def get_living_area(soup):
    #takes in soup object and returns the living area in sq feet as an int (alternative to building area)

    try:
        table_text=[item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='structured-amenities-table-category']
    
        for item in table_text:     
            item=item.lower()
            if 'living area' in item:
                i=item.index('living area')
                living_area=item[i:i+100]
                living_area=re.sub('\D', '', living_area)
        return float(living_area)
    except:
        return np.nan

  
#the function below is the main trulia web scraper function
def web_scraper(base_link, num_pages):
    #takes in the link for a trulia search and the number of pages of search 
    #results and returns a dataframe
    
    link_list=get_house_links(base_link, num_pages)
    dataframe=extract_link_data(link_list)
    return dataframe



