import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
import sys
import re
from io import StringIO, BytesIO
import datetime
import zipfile

# we can get PLZ info e.g. via deutschland, see https://pypi.org/project/deutschland/

# older data are here:
# https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/
# filenames like tageswerte_KL_00001_19370101_19860630_hist.zip

urlBase = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/"
# stationlist
stationList = "".join([urlBase,"KL_Tageswerte_Beschreibung_Stationen.txt"])

r = requests.get(stationList)

if r.status_code != 200:
    print("Stations failed")
    sys.exit()

stationData = r.text
stationData = re.sub(' +', ' ',stationData)
stationData = stationData.replace(" ",",").replace(",\r","").replace("\r","")
s = stationData.split("\n").copy()
stationData = ""
for l in s:
    ll = l.split(",")
    #print(ll)
    if len(ll) < 8:
        continue
    if len(ll)  > 8:
        # assume city has blank(s)
        head = ",".join(ll[:6])
        tail = ll[-1]
        city = "-".join(ll[6:-1]).replace(","," ")
        l1 = ",".join([head] + [city] + [tail])
        #print("merged:",l1)
    else:
        l1 = ",".join(ll)
    stationData = "\n".join([stationData,l1])
                
   
    
stations = pd.read_csv(StringIO(stationData)) 
stations.drop(index=0,inplace=True)
stations["start"] = pd.to_datetime(stations.von_datum)
stations["end"] = pd.to_datetime(stations.bis_datum)
stations.to_csv("stations.csv")

startDate = datetime.datetime(2021,1,1)
validStations = stations[stations.start <= startDate]
now = datetime.datetime.now()
endDate = now - datetime.timedelta(days=7)
validStations = validStations[stations.end >= endDate] #"20221012"] #now


def mkFile(x):
    return f"tageswerte_KL_{x:05}_akt.zip"

def extractKlima(klima):
    df0 = pd.read_csv(klima,sep=";")
    df0.fillna(-999)
    keys = ["TMK","TXK","TNK"]
    failed = False
    for key in keys:
        k = " " + key
        if k in df0.keys():
            df0.rename(columns={k : key},inplace = True)
        df0.drop(index = df0[df0[key] <= -999].index, inplace = True)
        
        if df0[key].empty:
            print("Empty ",key)
            failed = True
            
    if failed:
        return pd.DataFrame() # empty

    df = pd.DataFrame()
    df["Datum"] = df0.MESS_DATUM.astype(str).apply(pd.to_datetime)

    for key in keys:
        if key in df0.keys():
            df[key] = df0[key]
        else:
            df[key] = None

    df.rename(columns={"TMK":"Mean","TXK":"Max","TNK":"Min"},inplace = True)

    df = df.resample(on="Datum",rule="1W",origin="epoch").mean()
    df["ID"] = df0.STATIONS_ID.values[0].astype(str)

    return df


validStations["file"] = validStations.Stations_id.apply(mkFile)

validStations.to_csv("validStations.csv")


dwd = pd.DataFrame()

for f in validStations.file:
    url = "".join([urlBase,f])
    #print(url)
    r = requests.get(url)
    if r.status_code != 200:
        print(url, " failed")
        continue
    z = zipfile.ZipFile(BytesIO(r.content))
    content = z.namelist()
    for c in content:
        if c.startswith("produkt_klima"):
            #print("Extracting from ",c)
            klima = BytesIO(z.read(c))
            kdf = extractKlima(klima)
            if not kdf.empty:
                dwd = dwd.append(kdf)
            break
   

#sys.exit()

##files = os.listdir(".")
##dwd = pd.DataFrame()
##for f in files:
##    if not f.startswith("produkt_klima"):
##        continue
##    print(f)
##    kdf = extractKlima(klima)
##    if not kdf.empty:
##        dwd = dwd.append(kdf)
##

#dwd.resample(on="Datum",rule="1W",origin="epoch").mean()
#x = dwd.groupby(by="ID").resample(on="Datum",rule="1W",origin="epoch").mean()
# with early resampling Datum is a Datetimeindex already. not need to specify "ON"
#x = dwd.resample(rule="1W",origin="epoch").mean()
x = dwd.resample(rule="1W",origin=datetime.datetime(2021,1,1)).mean()
x["date"] = x.index # need a column
x["kw"] = pd.to_datetime(x.date).dt.isocalendar().week
x.to_csv("dwd-mean.csv")

fig = x.plot(y=["Mean","Max","Min"])
plt.show()

