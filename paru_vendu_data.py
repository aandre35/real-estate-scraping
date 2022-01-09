import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import requests_cache
import re
from tqdm import tqdm

requests_cache.install_cache("bases_scraping", expire_after=10e5)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def get_url(secteur, i):
    url = f"https://www.paruvendu.fr/immobilier/annonceimmofo/liste/listeAnnonces?tt=1&tbApp=1&tbDup=1&tbChb=1&tbLof=1&tbAtl=1&tbPla=1&tbMai=1&tbVil=1&tbCha=1&tbPro=1&tbHot=1&tbMou=1&tbFer=1&at=1&pa=FR&lol=0&ray=50&codeINSEE={secteur},,&p={i}"
    #print(url)
    return url

def get_nb_pages(secteur):
    response = requests.get(get_url(secteur, 0), headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    string = soup.find("div", class_="resume").span.text
    a = int(string.split("-")[0])
    b = int(string.split("-")[1].split("sur")[0])
    c = int(string.split("-")[1].split("sur")[1].replace("annonces","").replace(" ", ""))    
    
    return c // (b-a)

def get_df(secteur, nb_pages):
    
    # Initialisation
    prices = []
    surfaces = []
    types = []
    pieces = []
    cps = []
    
    # Scraping des données pour l'ensembles des annonces de chaque page
    for i in tqdm(range(1,nb_pages+1)):
        url = get_url(secteur, i)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        for annonce in soup.find_all('div', class_="ergov3-annonce"):
            try:
                # prix du bien
                price = annonce.find('div', class_="ergov3-priceannonce")
                price = int(price.text.replace(" ","").replace("€","").replace("\n","").replace("*","").replace("\r",""))
                #print(re.sub(r'(\s+){2,}|(\*)', ' ', annonce.find('div', class_='ergov3-priceannonce').text))

                # Titre de l'annonce. Permet de déduire le nombre de pièce, la surface et le type de bien
                txt = annonce.find('div', class_="ergov3-txtannonce")
                #print(re.sub(r"""[!?'".<>(){}@%&*/[/]""", " ",txt.h3.text ))
                # type de bien
                type_bien = txt.h3.text.split('\r\n')[1]

                # nombre de pièce du bien
                nb_pieces = txt.h3.text.split('\r\n')[2]

                # surface du bien
                surface = txt.h3.span.text.split(",")[-1].split("-")[-1].replace("m²","").replace(" ","").replace("\t","").replace("\n","").replace("\r","").replace("carrez","")

                # Code postal de l'annonce
                #cp = txt.cite.text.replace("(","").replace(")","").split(' ')[1].replace("\t","").replace("\n","").replace("\r","")
                cp = re.sub(r'[^\d]+', '', txt.cite.text)  
                if cp=='':
                    cp='0'
                # Ajout des caractéristiques dans des tableaux
                price = int(price)
                surface = int(surface)
                nb_pieces = int(nb_pieces)
                #type_bien = str(type_bien)
                #cps = int(cp)

                prices.append(price)
                surfaces.append(surface)
                pieces.append(nb_pieces)
                types.append(type_bien)
                cps.append(cp)

            except Exception as e:
                pass

    # Mise en forme des données sous la forme d'un dataframe pandas
    df = pd.DataFrame(data={
        "price": prices,
        "surface": surfaces,
        "pieces": pieces,
        "types": types,
        "code postal": cps,
    })

    # On ajoute le prix au m2 des logements
    df["prix au m2"] = df["price"]/df["surface"]
    
    # On modifie le type du code postal
    df['code postal'] = df['code postal'].astype(np.int32)
    df['pieces'] = df['pieces'].astype(np.int8)
    
    return df

def get_data_by_secteur(secteur):
    # Nombre de pages d'annonces pour le secteur choisi
    nb_pages = get_nb_pages(secteur)
    print("Nombre de pages trouvées ", nb_pages)
    # Téléchargement des données et construction du df
    df = get_df(secteur, nb_pages)
    return df

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    
    #secteur = "35XX0"
    secteur = "75000"
    df = get_data_by_secteur(secteur)
    
    # Sauvegarde du dataframe en csv
    df.to_csv('data/df_{}.csv'.format(secteur))
