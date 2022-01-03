import requests
from bs4 import BeautifulSoup

url="https://simulateur.tgvmax.fr/VSC/#/1/PARIS%20(intramuros)/RENNES"

# import du code de la page
response = requests.get(url)

print(response.text)

soup = BeautifulSoup(response.text, "html.parser")


items=soup.findAll('available')


print(items)