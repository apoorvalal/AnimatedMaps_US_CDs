# %% imports
import os, requests, re
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
# %% change path here
%cd /home/alal/tmp/scratch_data/US_CongressionalBoundaries/
# %%
def download(url):
    try:
        fn = url.rsplit('/', 1)[-1]
        r = requests.get(url)
        with open(fn,'wb') as f:
            f.write(r.content)
        print(url.rsplit('/', 1)[-1] + ' download successful.')
    except:
        print(url.rsplit('/', 1)[-1] + ' failed to download.')
        pass

def download_files(filelist):
    for f in filelist:
        download(f)
    return None
# %%
files = [f"https://cdmaps.polisci.ucla.edu/shp/districts{c:03d}.zip" for c in range(115)]
# %% download shapefiles
%cd shp/
download_files(files)

 ######   #######  ##    ##  ######   ##    ## ########    ###    ########   ######
##    ## ##     ## ###   ## ##    ##   ##  ##  ##         ## ##   ##     ## ##    ##
##       ##     ## ####  ## ##          ####   ##        ##   ##  ##     ## ##
##       ##     ## ## ## ## ##   ####    ##    ######   ##     ## ########   ######
##       ##     ## ##  #### ##    ##     ##    ##       ######### ##   ##         ##
##    ## ##     ## ##   ### ##    ##     ##    ##       ##     ## ##    ##  ##    ##
 ######   #######  ##    ##  ######      ##    ######## ##     ## ##     ##  ######


# %% cong - year crosswalk
# Make a request dictionary with all the parameters the Wikipedia API wants for requests to use
request = {}                         # Start with an empty dictionary
request['action'] = 'parse'          # Talk to the "parse" end-point of the API
request['format'] = 'json'           # Return the data in JSON format (for now)
request['prop'] = 'text|sections'    # Get the HTML markup of an article
request['formatversion'] = 2         # Output the data in a friendlier version
request['page'] = 'List of United States Congresses'
request['disabletoc'] = True         # Simplify things a bit
request['disableeditsection'] = True # Simplify things a bit
# Make the request to Wikipedia's API and use the .json() method to return JSON response to a Python dictionary
cong_json = requests.get('http://en.wikipedia.org/w/api.php', params=request).json()
# The HTML for the page lives in here as a big string
cong_html = cong_json['parse']['text']
# %%
cong_soup = BeautifulSoup(cong_html, "html.parser")
cong_tables = cong_soup.find_all('table')
print("There are a total of {0:,} tables in the data.".format(len(cong_tables)))
# %% extract and collapse
xw_big = pd.read_html(str(cong_tables[0]),header=0)[0]
xw_collapsed = xw_big.groupby("Congress").first().reset_index()
# %% extract congress number from string
num_finder = lambda  x : int(re.findall(r'\d+', x)[0])
xw_collapsed['cong'] = xw_collapsed.Congress.apply(num_finder)
# %% convert start date to datetime
xw_collapsed['startdate'] = pd.to_datetime(xw_collapsed['Congress began'])
xw_collapsed['enddate'] = pd.to_datetime(xw_collapsed['Congress ended'])
# %%
cong_timestamps = xw_collapsed[['cong', 'startdate', 'enddate']]
cong_timestamps = cong_timestamps.to_pickle("tmp/cong_time_xw.pkl")
# %%
