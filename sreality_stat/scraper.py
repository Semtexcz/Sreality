import math
import random
import re
import sys
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_soup_elements(typ_obchodu: str = "prodej", typ_stavby: str = "byty", pages: int = None) -> list:
    """

    :param typ_obchodu: "prodej" nebo "pronájem"
    :param typ_stavby: "byty" nebo "domy"
    :param pages: pocet stran, které chceme zpracovat, pro celé zpracování necháme nevyplněné
    :return: Vrací list, ve kterém jsou zapsány URL adresy jednotlivých inzerátů
    """
    browser = create_driver()

    ##########################################
    # 1. Volba Prodej/Pronájem, Byty/Domy,                 --Aukce/Bez Aukce (jen pro Prodeje) zatím nechávám být, cpe se mi to doprostřed url
    ##########################################

    url_x = r"https://www.sreality.cz/hledani"
    url = url_x + "/" + typ_obchodu + "/" + typ_stavby

    ##########################################
    # 2. načtení webu
    ##########################################

    browser.get(url)  # (url).text ??
    sleep(random.uniform(1.0, 1.5))
    innerHTML = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(innerHTML, 'html.parser')

    elements = []

    for link in soup.find_all('a', attrs={'href': re.compile(
            "^/detail/")}):  # !!!!!!!!!!!!!!!!! změněno, protože H2 neobsahovalo všechny věci, jen nadpis.
        link = link.get('href')
        elements.append(link)
    elements = elements[0::2] # každý odkaz se uloží dvakrát, proto se zde "maždou" duplicity

    ##########################################
    # 3. zjištění počtu listů - mělo by být optional, ale nevadí
    ##########################################
    records = soup.find_all(class_='numero ng-binding')[1].text
    records = re.split(r'\D', str(records))
    records = ",".join(records).replace(",", "")
    records = int(records)
    max_page = math.ceil(records / 20)
    print("----------------")
    print("Scrapuji: " + str(typ_obchodu) + " " + str(typ_stavby))
    print("Celkem inzerátů: " + str(records))
    print("Celkem stránek: " + str(max_page))

    ##########################################
    # 4. nastavení počtu stránek  -mělo být víc promakané
    ##########################################
    if not pages:
        pages = max_page

    print("Scrapuji (pouze) " + str(pages) + " stran.")
    print("----------------")

    ##########################################
    # 5. Scrapping zbylých listů - naštěstí v jednom okně
    ##########################################

    for i in range(pages - 1):
        i = i + 2

        sys.stdout.write('\r' + "Strana " + str(i - 1) + " = " + str(
            round(100 * (i - 1) / (pages), 2)) + "% progress. Zbývá cca: " + str(
            round(random.uniform(3.4, 3.8) * (pages - (i - 1)),
                  2)) + " sekund.")  # Asi upravím čas, na rychlejším kabelu v obýváku je to občas i tak 3 sec :O

        url2 = url + "?strana=" + str(i)
        browser.get(url2)

        sleep(random.uniform(1.0, 1.5))

        innerHTML = browser.execute_script("return document.body.innerHTML")
        soup2 = BeautifulSoup(innerHTML, 'html.parser')

        elements2 = []

        for link in soup2.findAll('a', attrs={'href': re.compile("^/detail/prodej/")}):
            link = link.get('href')
            elements2.append(link)

        elements2 = elements2[0::2]

        elements = elements + elements2  # tyto se už můžou posčítat, naštěstí, řpedtím než z nich budeme dělat elems = prvky třeba jména

    browser.quit()

    return elements


def elements_and_ids(x):
    elements = pd.DataFrame({"url": x})

    def get_id(x):
        x = x.split("/")[-1]
        return x

    elements["url_id"] = elements["url"].apply(get_id)

    len1 = len(elements)
    # Přidáno nově, v tuto chvíli odmažu duplikáty a jsem v pohodě a šetřím si čas dál.
    elements = elements.drop_duplicates(subset=["url", "url_id"], keep="first", inplace=False)
    len2 = len(elements)

    print("-- Vymazáno " + str(len1 - len2) + " záznamů kvůli duplikaci.")
    return elements


def create_driver():
    return webdriver.Chrome(ChromeDriverManager().install())
