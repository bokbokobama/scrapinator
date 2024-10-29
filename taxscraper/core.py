import pandas as pd
from tqdm import tqdm
import counties
import traceback


return_df = pd.DataFrame()


def scrape_data(id, countyName, numYears=-1):
    try:
        values, attrs = counties.fetchDataFromCounty(countyName, id)
        values = values.sort_values(by='Year',ascending=False)  
        if(numYears != -1):
            values = values.head(numYears)
            
        values = pd.DataFrame([[val for valRow in values.values.tolist() for val in valRow[1:]]],
                               columns = [f"{year} {key}" for year in values['Year'].values for key in counties.valueKeys[1:]])
        attrs = pd.DataFrame.from_dict(attrs, orient='index').T
        return(pd.concat([attrs, values], axis=1))

    except Exception as e: 
        return(pd.DataFrame.from_dict({'County': countyName,
                                       'Parcel ID': id,
                                       'Owner': type(e).__name__,
                                       'Address': str(e),
                                       'Tax District': traceback.format_exc()}, orient="index").T)



def iterateParcels(parcelList, countyName, numYears = -1):
    return_list = [scrape_data(parcel, countyName, numYears) for parcel in tqdm(parcelList)]
    return_df = pd.concat(return_list)
    return(return_df)
