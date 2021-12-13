# 3 = získání Souřadnic, Ceny a Popisu = z JSON
import json
import re

import requests

from sreality_stat.localization import get_address


def get_coords_price_meters(x):
    url = "https://www.sreality.cz/api/cs/v2/estates/" + str(x)
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=user_agent)
    byt = json.loads(response.text)
    coords = (str(byt.get("map", {}).get("lat", "")), str(byt.get("map", {}).get("lon", "")))
    price = byt.get("price_czk", {}).get("value_raw")
    # locality = byt.get("locality", {}).get("value") # TODO: naparsovat
    # items = byt.get("items", []) # TODO: naparsovat
    description = byt.get("meta_description")

    return coords, price, description


# Severní Šířka = latitude
# výchoDní / zápaDní Délka = longitude

def latitude(x):  # Rozdělí souřadnice na LAT a LON
    x = str(x).split()[0][1:8]
    return x


def longitude(x):
    x = str(x).split()[1][0:7]
    return x


#  4 = Prodej + Dům + Pokoje = z URL #################################################################################

def characteristics(x):
    x = x.split("/")
    buy_rent = x[2]
    home_house = x[3]
    rooms = x[4]

    return buy_rent, home_house, rooms


#  5 =  Plocha z Popisu ##############################################################################################

# Upraveno pro čísla větší než 1000 aby je to vzalo
# Zároveň se to vyhne velikost "Dispozice", "Atpyický", atd.

def plocha(x):
    try:
        metry = re.search(r'\s[12]\s\d{3}\s[m]', x)[
            0]  # SPecificky popsáno: Začíná to mezerou, pak 1 nebo 2, pak mezera, pak tři čísla, mezera a pak "m"
        metry = metry.split()[0] + metry.split()[1]  # Separuju Jedničku + stovky metrů, bez "m"
    except:
        try:
            metry = re.search(r'\s\d{2,3}\s[m]', x)[0]  # Mezera, pak 1-3 čísla, mezera a metr
            metry = metry.split()[0]  # Separuju čísla, bez "m"
        except:
            metry = -1
    return metry


def get_okres(PSC):
    if not PSC:
        return
    cislo = str(PSC)[1]
    if cislo == 0:
        return "Praha 10"
    else:
        return f"Praha {cislo}"


def parse_place(coords):
    new_coords = []
    for _ in coords:
        arr = _.split(".")
        if len(arr[1]) > 7:
            arr[1] = arr[1][:8]
        new_coords.append(".".join(arr))

    address = get_address(new_coords[0], new_coords[1])
    try:
        PSC = "".join([_ for _ in address.get("postcode") if
                       _.isnumeric()])  # address.get("postcode", "").replace(" ", "").replace("-", "")
    except Exception:
        PSC = None
    if PSC:
        PSC = int(PSC)
    ulice = address.get("road")
    obec = address.get("city") or address.get("town") or address.get("village")
    okres = address.get("municipality")
    kraj = address.get("county")
    if not okres and obec == "Hlavní město Praha":
        kraj = "Hlavní město Praha"
        obec = "Praha"
        okres = get_okres(PSC)

    if not kraj and str(PSC)[0] == "2":
        kraj = "Středočeský kraj"

    return ulice, obec, okres, kraj, PSC
