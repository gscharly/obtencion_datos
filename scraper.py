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

def obtener_link_lineas(url):
    soup = html(url)
    regex = re.compile('\/*aspx')
    regex3 = re.compile('listaBotones *')
    link_lineas = soup.find('div', attrs={'class': regex3}).find_all('a',attrs={'href': regex})
    patron = '\/.*aspx'
    link_lineas = [re.findall(patron, str(item)) for item in link_lineas]
    link_lineas = ['https://www.crtm.es/' + item[0] for item in link_lineas]
    print(link_lineas)
    return(link_lineas)

def obtener_nombre_paradas(url_lista):
    paradas_total = []
    for url in url_lista:
        soup = html(url)
        regex2 = re.compile('estaciones')
        paradas = soup.find('table', attrs={'class': 'tablaParadas'}).find_all('a', attrs={'href': regex2})
        paradas = [item.get_text() for item in paradas]
        paradas_total.append(paradas)
    print(paradas_total)

def obtener_orden_paradas(url_lista):
    orden_total = []
    for url in url_lista:
        soup = html(url)
        regex2 = re.compile('estaciones')
        paradas = soup.find('table', attrs={'class': 'tablaParadas'}).find_all('a', attrs={'href': regex2})
        orden = [(paradas.index(item) + 1) for item in paradas]
        orden_total.append(orden)
    print(orden_total)

def obtener_numero_linea(url_lista):
    numeros_lineas = []
    for url in url_lista:
        soup = html(url)
        numero_linea = soup.find('div', attrs={'class': 'brdGris2'}).find('h3', attrs={'class': 'titu4'}).find('span').get_text()
        numeros_lineas.append(numero_linea)
    print(numeros_lineas)

url_metro = 'https://www.crtm.es/tu-transporte-publico/metro/lineas.aspx'
url_ml = 'https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas.aspx'
url_cr = 'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas.aspx'


url_lista = obtener_link_lineas(url_cr)
obtener_nombre_paradas(url_lista)
obtener_orden_paradas(url_lista)
obtener_numero_linea(url_lista)



