import pandas as pd
import math
import pandasgui as gui
import matplotlib.pyplot as plt

dwd = pd.read_csv("dwd-mean.csv")
ind = pd.read_json("gasind.json")
prv = pd.read_json("gashouse.json")

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
# ratio of gas/temp °K
klima["ir"] = klima.ind/(klima.Mean + 273)
klima["pr"] = klima.prv/(klima.Mean + 273)

# special date string
def weekDt(x):
    return f'{int(x["kw"])}/{int(x["yr"])}'

klima["wk"] = klima.apply(weekDt,axis=1)

k = klima[["ir","pr","kw","yr"]]
#kk = k.sort_values(by=["kw","yr"]).groupby(by="yr").diff().fillna(0)
klima["t"] = klima.Mean * 100 # scale temperature by 100
klima.to_csv("klima.csv")
fig, axes = plt.subplots(nrows=3, ncols=1,sharex=True)

klima.plot(ax=axes[0],y=["ind","prv"])
klima.plot(ax=axes[1],y=["Mean","Min","Max"])
klima.plot(ax=axes[2],y=["ir","pr"])

plt.show()

# more analysis
k = klima.groupby(by="yr")[["ir","pr","kw","ind","prv","t","Mean"]]

yrs = [x for x,_ in k]
print("Years: ",yrs)

k21 = k.get_group(2021)
k22 = k.get_group(2022)

k21.set_index("kw",inplace=True)
k22.set_index("kw",inplace=True)

kk = k21.join(k22,how="inner",rsuffix="_r")

kk["idelta"] = (kk.ir_r - kk.ir)/kk.ir * 100.0
kk["pdelta"] = (kk.pr_r - kk.pr)/kk.pr * 100.0
kk["tdelta"] = (kk.t_r - kk.t)/100

kk.plot(y=["idelta","pdelta","tdelta","Mean"])

plt.show()
