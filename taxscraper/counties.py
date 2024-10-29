import cloudscraper
import pandas as pd
from io import StringIO
from urllib.parse import quote
import lxml

scraper = cloudscraper.create_scraper()
valueKeys = ['Year', 'Appraised Land', 'Appraised Building', 'Total Appraised',
             'Assessed Land',  'Assessed Building',  'Total Assessed']


def bulloch(id): # id = "S29 000007 000"
    url = f'https://qpublic.schneidercorp.com/Application.aspx?AppID=637&LayerID=11293&PageTypeID=4&PageID=4628&Q=256115977&KeyValue={id}'
    r = scraper.get(url).text # scrape url
    try: df_list = pd.read_html(StringIO(r))
    except(ValueError):
        raise ValueError(f"No data received from https://qpublic.schneidercorp.com/Application.aspx?AppID=637&LayerID=11293&PageTypeID=4&PageID=4628&Q=256115977&KeyValue={quote(id)}")
    
    values = df_list[-1].transpose().drop(2, axis = 1)[2:].assign(column1 = None, column2 = None, column3 = None)
    values, values.columns = values.reset_index(), valueKeys
    
    attributes = {'County': "Bulloch",
                  'Parcel ID': id,
                  'Owner': df_list[1][0][0],
                  'Address': df_list[0][1][1],
                  'Tax District': df_list[0][1][8],
                  'Class': df_list[0][1][5],
                  'Zoning': df_list[0][1][7]}
    return(values, attributes)


def cobb(id): # id = "20016301280"
    url = f'https://qpublic.schneidercorp.com/Application.aspx?AppID=1051&LayerID=23951&PageTypeID=4&PageID=9969&Q=1910122782&KeyValue={id}'
    r = scraper.get(url).text #scrape url
    try: df_list = pd.read_html(StringIO(r))
    except(ValueError):
        raise ValueError(f"No data received from https://qpublic.schneidercorp.com/Application.aspx?AppID=1051&LayerID=23951&PageTypeID=4&PageID=9969&Q=1910122782&KeyValue={quote(id)}")

    values = pd.merge(df_list[3], #merge relevant lists 
                      df_list[5],
                      how = "outer",
                      on = "Year",
                      suffixes = ("_Appraised", "_Assessed"))
    values = values.drop(["Property Class", "LUC"], axis = 1)
    values.columns = valueKeys
    
    attributes = {'County': "Cobb",
                  'Parcel ID': id,
                  'Owner': "",
                  'Address': df_list[0][1][1],
                  'Tax District': df_list[0][1][7],
                  'Class': df_list[3].iloc[0,1],
                  'LUC': df_list[3].iloc[0,2]}
    return(values, attributes)

#cobb("20016301280")[1]


def dekalb(id): # id = "18 100 02 005"
    url = f'https://propertyappraisal.dekalbcountyga.gov/datalets/datalet.aspx?mode=value_history_main&UseSearch=no&pin={id}'
    r = scraper.get(url).text # scrape url
    df_list = pd.read_html(StringIO(r))
    if(df_list[5].shape[1] <= 1):
        raise ValueError(f"No data received from https://gwinnettassessor.manatron.com/IWantTo/PropertyGISSearch/PropertyDetail.aspx?p={quote(id)}. Is this a valid parcel?")
    
    values = pd.merge(df_list[5][1:-1],
                      df_list[7][1:-1].drop(1, axis = 1),
                      how = "outer",
                      on = 0).drop([1], axis=1) # merge relevant lists
    values.columns = valueKeys 

    attributes = {'County': "Dekalb",
                  'Parcel ID': id,               
                  'Owner': df_list[3][0][3],
                  'Address': df_list[3][2][3],
                  'Tax District': df_list[3][0][2],
                  'Class': df_list[5][1][1],
                  'LUC': ""}
    return(values, attributes)


def gwinnett(id): # id = "R6052 140"
    url = f'https://gwinnettassessor.manatron.com/IWantTo/PropertyGISSearch/PropertyDetail.aspx?p={id}'
    r = scraper.get(url).text #scrape url
    df_list = pd.read_html(StringIO(r))
    if(len(df_list) <= 1):
        raise ValueError(f"No data received from https://gwinnettassessor.manatron.com/IWantTo/PropertyGISSearch/PropertyDetail.aspx?p={quote(id)}")
    
    values = pd.concat([df_list[2][1:5],df_list[2][6:]]).transpose()
    values = values[1:].reset_index()
    values.columns = valueKeys

    attributes = {'County': "Gwinnett",
                  'Parcel ID': id,
                  'Owner': df_list[1][0][0][:df_list[1][0][0].find(df_list[1][2][3])-1],
                  'Address': df_list[1][2][3],
                  'Tax District': df_list[1][2][5],
                  'Class': df_list[1][2][4],
                  'Land Type': df_list[10]['Land Type'][0]}
    return(values, attributes)


countyFunctions = {"bulloch": bulloch,
                   "cobb": cobb,
                   "dekalb": dekalb,
                   #"fulton": fulton,
                   "gwinett": gwinnett}

def fetchDataFromCounty(countyName, id):
    match countyName.lower():
        case countyName if countyName.lower() in countyFunctions:
            return(countyFunctions[countyName](id))
        case _: raise ValueError("County name not recognized")