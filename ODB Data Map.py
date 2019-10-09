import requests, re, json, os
import pandas as pd
from bs4 import BeautifulSoup

# where the data map csv should write out to
write_to_path = '/home/dan/Python/PythonCode/Open Data Buffalo Docs/'

target_urls = [
        "https://data.buffalony.gov/Quality-of-Life/311-Service-Requests/whkc-e5vr"
        ,"https://data.buffalony.gov/Transportation/Annual-Average-Daily-Traffic-Volume-Counts/y93c-u65y"
        ,"https://data.buffalony.gov/Quality-of-Life/Code-Violations/ivrf-k9vm"
        ,"https://data.buffalony.gov/Public-Safety/Crime-Incidents/d6g9-xbgu"
        ,"https://data.buffalony.gov/Quality-of-Life/Monthly-Recycling-and-Waste-Collection-Statistics/2cjd-uvx7"
        ,"https://data.buffalony.gov/Transportation/Parking-Summonses/yvvn-sykd"
        ,"https://data.buffalony.gov/Economic-Neighborhood-Development/Permits/9p2d-f3yt"
              ]

#########################################

def find_elements(url):
    
    # make request
    result = requests.get(url)
    soup = BeautifulSoup(result.content,'html.parser')

    # get dataset name (from page title)
    dataset_name = soup.title.string
    dataset_name = dataset_name[0:dataset_name.find('|')-1]

    # get json element out of from url source code
    script = soup.find('script', text=re.compile('initialState'))
    script_text = script.text
    start = script_text.find('{')
    stop = script_text.rfind('}')
    str_for_json = script_text[start:stop+1]

    # load json
    JSON = json.loads(str_for_json)

    # how many columns are there in this dataset?
    records = len(JSON["view"]["columns"])

    # create list of all columns in the datset    
    col_names = []
    for n in range(records):
        col_name = JSON["view"]["columns"][n]["name"]
        col_names.append(col_name)

    # prepare the df
    df = pd.DataFrame(col_names, columns =['ColName'])

    # add dataset name, and hard code a '1' for a marker (needed later for pivot table) 
    df["Dataset"], df["Mark"]= dataset_name,1

    return(df)

#########################################

# create df for each url, and append them into a list
dataframes = []
for url in target_urls:
    dataframes.append(find_elements(url))

# create master df by concatenating all dfs from the list together
main = pd.concat(dataframes,ignore_index=True)

# all caps the data fields/column names
main["ColName"] = main["ColName"].str.upper()

# pivot the df, placing ColName in the row labels, Dataset name as column label, and 'Mark' (hard coded 1) at intersections
df = pd.pivot_table(main,index="ColName", columns="Dataset",values="Mark")

# write out to csv
df.to_csv(os.path.join(write_to_path,"ODB Data Map.csv"))
