import pathlib
import re
import time

import pandas as pd
from geopy.exc import GeocoderTimedOut  # for Error handling
from geopy.geocoders import Nominatim  # Geolocator   # pip install geopy


# 6 = Adresy z předešlých inzerátů a short_coords

# Vytvoření ořezaných souřadnic, přesnost je dostatečná, lépe se najdou duplikáty
def short_coords(x):
    """
    x = x.astype(str)   # Bylo potřeba udělat string - ale Tuple se blbě převádí - vyřešil jsem uložením a načtením skrz excel
    """

    x1 = re.split(r'\W+', x)[1] + "." + re.split(r'\W+', x)[2]
    x1 = round(float(x1), 4)

    x2 = re.split(r'\W+', x)[3] + "." + re.split(r'\W+', x)[4]
    x2 = round(float(x2), 4)

    return x1, x2


#############################

# Napmapuje až 80 % Adres z předešlých inzerátů
def adress_old(x):
    path = pathlib.Path(__file__).parent / "data" / "Adresy.xlsx"
    adresy = pd.read_excel(str(path))
    adresy = adresy[["oblast", "město", "okres", "kraj", "url_id", "short_coords"]]

    # Nejlepší napárování je toto:
    # alternativně Inner a Left minus řádky s NaNs a funguje stejně)

    x.short_coords = x.short_coords.astype(
        str)  # získat string na souřadnice, protože v Načteném adresáři je mám už taky jako string
    data = pd.merge(x, adresy, on=["short_coords", "url_id"],
                    how="left")  # upraveno matchování na url_ID + short_coords, je to tak iv Adresáří, je to jednoznačné, jsou tam unikátní.
    # Pokud si v dalším kroku dostáhnu ke starému url_id a k nové coords ještě novou adresu, tak pak se mi uloží do Adresáře nová kombiance ID + short_coord a je to OK
    # Viz funkce"update_databáze_adres() kde je totéž info

    print("-- Počet doplněných řádků je: " + str(len(data[~data.kraj.isna()])) + ", počet chybějících řádků je: " + str(
        len(data[data.kraj.isna()])))

    return data


# 7 = Adresy - zbývající přes GeoLocator ###############################################################################################################################

def adress_new(x):
    # Pozn. - je to random, závislost rychlosti na user_agent, i na format_string se nepovedlo potvrdit - ale dokumentace user-agent uvíádí jako povinnost
    # Timeout na 20s  zrušil Errory - None záleží na verzi geopy !! viz dokumentace
    # Rychlost a úspěch velmi záleží na připojení. Ryhlost 0.2s - 10s na záznam.
    # Problém s Too many requests se "spraví přes noc", kdyžtak - nebo viz stackoverflow - nastavit user-agent (https://stackoverflow.com/questions/22786068/how-to-avoid-http-error-429-too-many-requests-python)

    geolocator = Nominatim(timeout=20, user_agent="JZ_Sreality")  # Pomohlo změnit jméno, proti "Error 403" !!
    location = geolocator.reverse(x.strip("())"))
    # Reverse samotné znamená obrácené vyhleádvání = souřadnice -> Adresa
    try:
        oblast = location[0].split(",")[-7]
    except:
        oblast = -1
    try:
        město = location[0].split(",")[-6]
    except:
        město = -1
    try:
        okres = location[0].split(",")[-5]
    except:
        okres = -1
    try:
        kraj = location[0].split(",")[-4]
    except:
        kraj = -1

    time.sleep(0.5)
    return oblast, město, okres, kraj


##################################################################

# Pomocná funkce, opakuje předchozí funkci pořád dokola dokud neprojde bez Erroru
def repeat_adress(x):
    try:
        x["oblast"], x["město"], x["okres"], x["kraj"] = zip(*x['coords'].map(adress_new))
    except GeocoderTimedOut:
        print("Another try")
        x["oblast"], x["město"], x["okres"], x["kraj"] = zip(*x['coords'].map(adress_new))


# 8 = Merging adres
# Aplikuje předchozí funkci pouze na řídky, které ještě nemají doplněné adresy z kroku 6.)

def adress_merging(x):
    data_new = x.copy()
    bool_series = pd.isnull(data_new.kraj)
    data_new = data_new[bool_series]  # subset s chybějícími adresami

    repeat_adress(data_new)

    data_all = pd.concat([x, data_new])
    data_all = data_all[~pd.isnull(data_all.kraj)]
    data_all = data_all.sort_index()

    data = data_all.copy()

    return data


def get_address(lat, long):
    geolocator = Nominatim(timeout=20, user_agent="JZ_Sreality")  # Pomohlo změnit jméno, proti "Error 403" !!
    location = geolocator.reverse(f"{lat}, {long}")
    return location.raw["address"]
