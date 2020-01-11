from bs4 import BeautifulSoup
import urllib.request
import re

def html(url):
    try:
        page = urllib.request.urlopen(url)
    except:
        print("Se ha producido un error.")

    soup = BeautifulSoup(page, 'html.parser')

    return (soup)

url_metro = 'https://www.crtm.es/tu-transporte-publico/metro/lineas.aspx'
url_ml = 'https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas.aspx'
url_cercanias = 'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas.aspx'

soup = html(url_metro)

numero_linea = soup.find_all('span', attrs={'class': 'logo'})
numero_linea = [item.get_text() for item in numero_linea]
print(numero_linea)

regex = re.compile('\/*aspx')
link_linea = soup.find('div', attrs={'class':'listaBotones logosCuadrado dosCols'}).find_all('a', attrs={'href': regex})
patron = '\/.*aspx'
link_linea = [re.findall(patron, str(item)) for item in link_linea]
link_linea = ['https://www.crtm.es/' + item[0] for item in link_linea]
print(link_linea)

linea = link_linea[0]
soup = html(linea)
regex2 = re.compile('estaciones')
paradas = soup.find('table', attrs={'class':'tablaParadas'}).find_all('a', attrs={'href': regex2})
paradas = [item.get_text() for item in paradas]
print(paradas)