import pandas as pd
import math
import pandasgui as gui
import matplotlib.pyplot as plt

dwd = pd.read_csv("dwd-mean.csv")
ind = pd.read_json("../bnetza/gasind.json")
prv = pd.read_json("../bnetza/gashouse.json")

bi = pd.DataFrame(columns=["yr","kw","ind"])
for i in ind.itertuples():
    bi = bi.append({"yr":2021,"kw":i.KW,"ind":i[3]},ignore_index=True)
    if not math.isnan(i[2]):
        bi = bi.append({"yr":2022,"kw":i.KW,"ind":i[2]},ignore_index=True)
bi.sort_values(by=["yr","kw"],inplace=True)
bi.reset_index(inplace=True,drop=True)
                     
bp = pd.DataFrame(columns=["yr","kw","prv"])
for i in prv.itertuples():
    bp = bp.append({"yr":2021,"kw":i.KW,"prv":i[3]},ignore_index=True)
    if not math.isnan(i[2]):
        bp = bp.append({"yr":2022,"kw":i.KW,"prv":i[2]},ignore_index=True)
                     
bp.sort_values(by=["yr","kw"],inplace=True)
bp.reset_index(inplace=True,drop=True)

bna = pd.merge(bi,bp)
bna["sum"] = bna.ind + bna.prv

bna.to_csv("bna.csv")

# 
dwd.sort_values(by=["yr","kw"],inplace=True)
dwd.reset_index(inplace=True,drop=True)

# get lowest week of dwd in first year
dwdmin = int(dwd[dwd.yr == 2021].kw.min())

bnamin = bna[bna.kw == dwdmin].index.values[0]
bna.drop(index=range(bnamin),inplace=True)
bna.reset_index(inplace=True,drop=True)

if len(dwd) > len(bna):
    dwd.drop(index=list(range(len(bna),len(dwd))),inplace=True)
    
klima = pd.merge(bna,dwd)
klima["t"] = klima.Mean * 100 # scale temperature by 100
klima.to_csv("klima.csv")
klima.plot(y=["t","ind","prv"])
plt.show()
