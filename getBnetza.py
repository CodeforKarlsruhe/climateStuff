import requests
import pandas as pd

# https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Versorgungssicherheit/aktuelle_gasversorgung/_downloads/09_September/220929_gaslage.pdf?__blob=publicationFile&v=3

# https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Versorgungssicherheit/aktuelle_gasversorgung/_downloads/10_Oktober/221004_gaslage.pdf?__blob=publicationFile&v=3
# Seite mit Auswahl
# https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Versorgungssicherheit/aktuelle_gasversorgung_/_svg/Gasimporte/Gasimporte.html

M = ["Januar","Februar","Maerz","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]

def mkUrl(day,mon,yr):
    return f"https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Versorgungssicherheit/aktuelle_gasversorgung/_downloads/{mon:02}_{M[mon - 1]}/{yr}{mon:02}{day:02}_gaslage.pdf?__blob=publicationFile&v=3"

print(mkUrl(4,10,22))

print(mkUrl(24,1,22))


# also interesting:
# https://www.tradinghub.eu/de-de/Ver%C3%B6ffentlichungen/Transparenz/Marktgebietsmonitor
# get https://datenservice-api.tradinghub.eu/api/evoq/GetMarktgebietsmonitorTabelle?DatumStart=01-01-2022&DatumEnde=10-07-2022&_=1665239899723
# liefert json

"""
In diesem Bereich veröffentlicht Trading Hub Europe den Marktgebietsmonitor, der die Gastransportdaten
in und aus dem Marktgebiet sowie den SLP- sowie RLM-Verbrauch erfasst. 

Trading Hub Europe greift hierzu u.a. auf die Daten der API-Schnittstelle von ENTSOG zurück.
Bitte beachten Sie, dass die Trading Hub Europe keine Gewähr für die Richtigkeit dieser außerhalb
des Einflussbereiches der Trading Hub Europe liegenden Informationen übernehmen kann.
Trading Hub Europe kann keine Qualitätssicherung der Daten vornehmen. 

HINWEIS: 
Bitte beachten Sie, dass die Daten des Marktgebietsmonitors aktuell unvollständig sind.
Dies gilt insbesondere für weniger als 3 Tage zurückliegende Werte.
Das in der grafischen Darstellung ausgewiesene "Gesamt-Delta" stellt die Differenz der
in der Darstellung aufgeführten Einspeisungen und Ausspeisungen dar.

"""


# aggregated consumption
# https://datenservice-api.tradinghub.eu/api/evoq/GetAggregierteVerbrauchsdatenChart?DatumStart=10-01-2022
# https://datenservice-api.tradinghub.eu/api/evoq/GetAggregierteVerbrauchsdatenTabelle?DatumStart=10-01-2022&DatumEnde=10-31-2022&GasXType_Id=all&_=1665240414824
# https://datenservice.tradinghub.eu/Dokumente/The_XML_Interface_V1.0_de.pdf
"""
In diesem Bereich veröffentlicht Trading Hub Europe die aggregierten Verbrauchsdaten (Allokationsdaten) für
SLP sowie RLM Entnahmestellen im Marktgebiet Trading Hub Europe. Diese aggregierten Verbrauchsdaten beruhen
auf den Allokationsdaten, die die Netzbetreiber an Trading Hub Europe übermitteln.  Die Veröffentlichung der
vorläufigen SLP Daten erfolgt täglich für den Folgetag, die Veröffentlichung der vorläufigen RLM Daten täglich
für den Vortag. Korrigierte RLM Daten werden nach Übermittlung der M+12WT Meldung veröffentlicht.
Die Veröffentlichung der finalen Werte erfolgt nach Abschluss der Clearingfristen.
"""
the = {
"marktmon" : "https://datenservice-api.tradinghub.eu/api/evoq/GetMarktgebietsmonitorTabelle?DatumStart=01-01-2020&DatumEnde=10-31-2022",
"aggcons" : "https://datenservice-api.tradinghub.eu/api/evoq/GetAggregierteVerbrauchsdatenTabelle?DatumStart=01-01-2020&DatumEnde=10-31-2022&GasXType_Id=all"
}

for k in the.keys():
    df = pd.read_json(the[k])
    #df.to_json(".".join([k,"json"]))
    df.to_json(".".join([k,"json"]),orient="records")

bnetza = {	
# gasimport
"gasimp" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081248",

# gasexport
"gasexp" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081194",

# gasförderung
"gasprod" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081200",

# gasfüllstand
"gasfill" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081180",

# gas consum indistry
"gasind" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081204",

# gasverbrauch haushalt + gewerbe
"gashouse" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081246",

# gasverbruach gesamt
"gascons" : "https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081208",
}

for k in bnetza.keys():
    df = pd.read_csv(bnetza[k],sep=";")
    if k == "gasind" or k == "gashouse" or k == "gascons":
        date = "KW"
    else:
        date = "Date"
    df.rename(columns={".":date},inplace=True)
    df.to_json(".".join([k,"json"]),orient="records")

