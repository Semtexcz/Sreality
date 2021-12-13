import pathlib

import arrow

from sreality_stat.parser import get_coords_price_meters, characteristics, plocha, parse_place
from sreality_stat.scraper import get_soup_elements, elements_and_ids


def run():
    data = scrap_all()
    now = str(arrow.now()).split("T")[0]
    path = pathlib.Path(__file__).parent / "data" / f"{now}_estates"
    data.to_csv(str(path))


def scrap_all(typ_obchodu="prodej", typ_stavby="byty", pages=None):
    # Scrapni data - hezky komunikuje = cca 50 min
    data = get_soup_elements(typ_obchodu=typ_obchodu, typ_stavby=typ_stavby,
                             pages=pages)  # vrátí ULR adresy jednotliých inzerátů
    print("1/8 Data scrapnuta, získávám URLs.")

    # 2 = Získání URLS
    data = elements_and_ids(data)
    # data.to_excel(r"a1_URLs_prodej_byty.xlsx")
    print("2/8 Získány URL, nyní získávám Souřadnice, Ceny a Popis - několik minut...")

    # 3 = získání Souřadnic, Ceny a Popisu = z JSON
    data["coords"], data["cena"], data["popis"] = zip(*data['url_id'].map(get_coords_price_meters))
    print("3/8 Získány Souřadnice, Ceny a Popis, nyní získávám informace z URLs.")

    # 4 = Prodej + Dům + Pokoje = z URL
    data["prodej"], data["dům"], data["pokoje"] = zip(*data['url'].map(characteristics))
    print("4/8 Získány informace z URLs, nyní získávám informace z popisu.")

    # 5 =  Plocha z Popisu
    data["plocha"] = data['popis'].apply(plocha)
    print("5/8 Získány informace z Popisu, nyní mapuji Adresy z předešlých inzerátů.")

    # 6 Adresy
    data["ulice"], data["obec"], data["okres"], data["kraj"], data["PSČ"] = zip(*data["coords"].map(parse_place))

    return data


if __name__ == '__main__':
    run()
