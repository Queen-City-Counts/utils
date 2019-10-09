import json, re, urllib.request, datetime, os
import pandas as pd
from bs4 import BeautifulSoup

# where the data map csv should write out to
write_to_path = "/home/dan/Python/PythonCode/Open Data Buffalo Docs/"

target_urls = [
        "https://data.buffalony.gov/Quality-of-Life/311-Service-Requests/whkc-e5vr"
        ,"https://data.buffalony.gov/Transportation/Annual-Average-Daily-Traffic-Volume-Counts/y93c-u65y"
        ,"https://data.buffalony.gov/Quality-of-Life/Code-Violations/ivrf-k9vm"
        ,"https://data.buffalony.gov/Public-Safety/Crime-Incidents/d6g9-xbgu"
        ,"https://data.buffalony.gov/Quality-of-Life/Monthly-Recycling-and-Waste-Collection-Statistics/2cjd-uvx7"
        ,"https://data.buffalony.gov/Transportation/Parking-Summonses/yvvn-sykd"
        ,"https://data.buffalony.gov/Economic-Neighborhood-Development/Permits/9p2d-f3yt"
              ]


def get_and_append(url):

        # do not allow Nulls into any dicts (otherwise, this function can error out)  
        class BlankDict(dict):
                def __missing__(self,key):
                        return 'None'

        # make request
        response = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(response, 'html.parser')

        # get json element out of from url source code
        script = soup.find('script', text=re.compile('initialState'))
        script_text = script.text
        start = script_text.find('{')
        stop = script_text.rfind('}')
        str_for_json = script_text[start:stop+1]

        # get dataset name (from page title)
        dataset_name = soup.title.string
        dataset_name = dataset_name[0:dataset_name.find("|")-1]


        #########################################
        # extract from json file all information needed for the data dictionary 
        # load json
        JSON = json.loads(str_for_json, object_hook=BlankDict)

        # get dataset desc
        dataset_desc = JSON["view"]["description"]

        # get dataset limitations
        try:
                limitations = JSON["view"]["metadata"]["custom_fields"]["Disclaimers"]["Limitations"]
        except:
                limitations = "None"
                pass

        # get other items of interest from the url
        goes_back_to = JSON["view"]["metadata"]["custom_fields"]["Dataset Information"]["Data Series Start Date"]
        update_frequency = JSON["view"]["metadata"]["custom_fields"]["Dataset Information"]["Update Frequency"]
        auto_updated = JSON["view"]["metadata"]["custom_fields"]["Dataset Information"]["Automated"]
        dataset_key = url[url.rfind("/")+1:]
        api_url = JSON["view"]["apiFoundryUrl"]
        retrieved = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        last_updated = JSON["view"]["lastUpdatedAt"]
        last_updated_fmt = last_updated[0:last_updated.find('T')]
        #########################################
        

        #########################################
        # collect any notes (there may be none, there may be multiple)
        notes = JSON["view"]["metadata"]["custom_fields"]["Notes"]
        notes_list = []
        try:
                for x,y in notes.items():
                        notes_list.append(str(y))
        except:
                notes_list.append("None")
        #########################################


        #########################################
        # make table showing name, description, and api call name for each col in the dataset
        # make list of all column names on this url
        records = len(JSON["view"]["columns"])
        col_names = []
        for n in range(records):
                col_name = JSON["view"]["columns"][n]["name"]
                col_names.append(col_name)

        # make list of all data fields descriptions on this url
        col_descs = []
        for d in range(records):
                try:
                        desc_name = JSON["view"]["columns"][d]["description"]
                        col_descs.append(desc_name)
                except:
                        pass
                
        # make list of all api names on this url
        col_api_name = []
        for a in range(records):
                api_name = JSON["view"]["columns"][a]["fieldName"]
                col_api_name.append(api_name)

        # combine the above three lists into one df
        data_dict = pd.DataFrame(list(zip(col_names, col_descs, col_api_name)), columns =['Name', 'Desc', 'API_name'])
        pd.set_option('display.max_colwidth', -1)

        # create html of table
        table = data_dict.to_html(classes='table table-striped', escape=False, index=False)
        #########################################

        # generate html for text
        html = f'''
        <html>
        <body style="font-family:Helvetica">
        <h1>{dataset_name}</h1>
        <table width="800">
        <tbody>
        <tr>
        <td><u>Data retrieved on</u>: {retrieved}</td>
        <td><u>Data goes back to</u>: {goes_back_to}</td>
        </tr>
        <tr>
        <td><u>Automatically updated</u>: {auto_updated}</td>
        <td><u>Last updated on</u>: {last_updated_fmt}</td>
        </tr>
        <tr>
        <td><u>Update frequency</u>: {update_frequency}</td>
        <td><u>Dataset Key</u>: {dataset_key}</td>
        </tr>
        </tbody>
        </table>
        <p><u>Dataset URL</u>: {url}</p>
        <p><u>API URL</u>: {api_url}</p>
        <h3><u>Description</u></h3>
        <p>{dataset_desc}</p>
        <h3><u>Data Dictionary</u></h3>
        <p>{table}</p>
        <h3><u>Limitations</u></h3>
        <p>{limitations}</p>
        <h3><u>Notes</u></h3>
        <p>{'  '.join(str(x) for x in notes_list)}</p>
        <br>
        <hr>
        <br>
        </body>
        </html>
        '''

        # append html text for this dataset to the master html document
        MASTER = open(os.path.join(write_to_path,"MASTER.html"), "a+")
        MASTER.write(html)
        MASTER.close()

        # create html file for each individual dataset
        # (if the dataset has a '/' in its name, this will error out, so replace all '/' with '.') 
        if "/" in dataset_name:
                dataset_name = dataset_name.replace("/",".")
        individual = open(os.path.join(write_to_path,str(dataset_name+".html")), "w+")
        individual.write(html)
        individual.close()

# run through all urls in the target_urls list        
for url in target_urls:
        get_and_append(url)
