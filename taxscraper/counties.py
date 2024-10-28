import cloudscraper, requests, lxml
import pandas as pd
import traceback
from io import StringIO
from urllib.parse import quote
import re

scraper = cloudscraper.create_scraper()
keys = ["Input", "Tax ID", "County", "Tax District", "Owner", "Address", "Tax Year", "Class",
        "Appraised Land", "Appraised Building", "Appraised Total", "Assessed Land", "Assessed Building", "Assessed Total"]


def scrape_data(id, countyName = False, mostRecentYearOnly = False):
    try:
        if not countyName:
            match id.lower():
                case _ if re.match(r"^[A-z]\d{2} \d{6} \d{3}$", id): values, attributes = bulloch(id)
                case _ if re.match(r"^\d{11}$", id): values, attributes = cobb(id)
                case _ if re.match(r"^\d{2} \d{3} \d{2} \d{3}$", id): values, attributes = dekalb(id)
                case _ if re.match(r"^[A-Z]\d{4} \d{3}$", id): values, attributes = gwinnett(id)
                case _: raise ValueError("Parcel ID string did not match recognized patterns")
        else:
            match countyName.lower():
                case "bulloch": values, attributes = bulloch(id)
                case "cobb": values, attributes = cobb(id)
                case "dekalb": values, attributes = dekalb(id)
                case "fulton": values, attributes = fulton(id, 2024)
                case "gwinnett": values, attributes = gwinnett(id)
                case _: raise ValueError("County name not recognized")
        
        df = pd.concat([pd.concat([attributes] * len(values), ignore_index=True), values], 
                       axis=1).set_axis(keys, axis=1).sort_values(by=['Tax Year'])
        if(mostRecentYearOnly): df = df[0]
        return(df)

    except Exception as e: 
        #print(traceback.format_exc())
        return(pd.DataFrame([[id, "", type(e).__name__, str(e),
                              traceback.format_exc()] + [""]*(len(keys)-5)],
                            columns=keys))
    


def bulloch(id): # id = "S29 000007 000"
    url = f'https://qpublic.schneidercorp.com/Application.aspx?AppID=637&LayerID=11293&PageTypeID=4&PageID=4628&Q=256115977&KeyValue={id}'
    r = scraper.get(url).text # scrape url
    try: df_list = pd.read_html(StringIO(r))
    except(ValueError):
        raise ValueError(f"No data received from https://qpublic.schneidercorp.com/Application.aspx?AppID=637&LayerID=11293&PageTypeID=4&PageID=4628&Q=256115977&KeyValue={quote(id)}")
    
    values = df_list[-1].transpose().drop(2, axis = 1)[2:].assign(column1 = None, column2 = None, column3 = None)
    values.insert(0, 'Class', df_list[0][1][5])
    values = values.reset_index()
    
    attributes = pd.DataFrame({'Input': id, # create a new df containing attribute data
                                'Tax ID': df_list[0][1][0],
                                'County': "Bulloch",
                                'Tax District': df_list[0][1][8],
                                'Owner': df_list[1][0][0],
                                'Address': df_list[0][1][1]}, index =[0])

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
                        on = "Year")
    values = values.drop("LUC", axis = 1) #drop irrelevant columns
    
    attributes = pd.DataFrame({'Input': id, #create a new df containing attribute data
                                'Tax ID': df_list[0][1][0],
                                'County': "Cobb",
                                'Tax District': df_list[0][1][7],
                                'Owner': "",
                                'Address': df_list[0][1][1]}, index =[0])
    return(values, attributes)


def dekalb(id): # id = "18 100 02 005"
    url = f'https://propertyappraisal.dekalbcountyga.gov/datalets/datalet.aspx?mode=value_history_main&UseSearch=no&pin={id}'
    r = scraper.get(url).text # scrape url
    df_list = pd.read_html(StringIO(r))
    if(df_list[5].shape[1] <= 1):
        raise ValueError(f"No data received from https://gwinnettassessor.manatron.com/IWantTo/PropertyGISSearch/PropertyDetail.aspx?p={quote(id)}. Is this a valid parcel?")
    
    values = pd.merge(df_list[5][1:-1],
                        df_list[7][1:-1].drop(1, axis = 1),
                        how = "outer",
                        on = 0,
                        suffixes = ("_Appraised", "_Assessed")) # merge relevant lists 
    
    attributes = pd.DataFrame({'Input': id, # create a new df containing attribute data
                                'Tax ID': df_list[3][0][0],
                                'County': "Dekalb",
                                'Tax District': df_list[3][0][2],
                                'Owner': df_list[3][0][3],
                                'Address': df_list[3][2][3]}, index=[0])
    return(values, attributes)


def gwinnett(id): # id = "R6052 140"
    url = f'https://gwinnettassessor.manatron.com/IWantTo/PropertyGISSearch/PropertyDetail.aspx?p={id}'
    r = scraper.get(url).text #scrape url
    df_list = pd.read_html(StringIO(r))
    if(len(df_list) <= 1):
        raise ValueError(f"No data received from https://gwinnettassessor.manatron.com/IWantTo/PropertyGISSearch/PropertyDetail.aspx?p={quote(id)}")
    
    values = pd.concat([df_list[2][1:4],df_list[2][5:]]).transpose()
    values, values.columns = values[1:] , values.iloc[0]
    values.insert(1, 'Class', df_list[1][2][4])
    values = values.reset_index()

    attributes = pd.DataFrame({'Input': id, #create a new df containing attribute data
                                'Tax ID': df_list[1][2][1],
                                'County': "Gwinnett",
                                'Tax District': df_list[1][2][5],
                                'Owner': df_list[1][0][0],
                                'Address': df_list[1][2][3]}, index=[0])
    return(values, attributes)


def tf(num): return("\x1b["+str(num)+"m")