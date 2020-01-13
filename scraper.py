from bs4 import BeautifulSoup
import urllib.request
import re
import pandas as pd

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
    return(link_lineas)

def obtener_nombre_paradas(url_lista):
    paradas_total = []
    for url in url_lista:
        soup = html(url)
        regex2 = re.compile('estaciones')
        paradas = soup.find('table', attrs={'class': 'tablaParadas'}).find_all('a', attrs={'href': regex2})
        paradas = [item.get_text() for item in paradas]
        paradas_total.append(paradas)
    return(paradas_total)

def obtener_orden_paradas(url_lista):
    orden_total = []
    for url in url_lista:
        soup = html(url)
        regex2 = re.compile('estaciones')
        paradas = soup.find('table', attrs={'class': 'tablaParadas'}).find_all('a', attrs={'href': regex2})
        orden = [(paradas.index(item) + 1) for item in paradas]
        orden_total.append(orden)
    return(orden_total)

def obtener_numero_linea(url_lista):
    numeros_lineas = []
    for url in url_lista:
        soup = html(url)
        numero_linea = soup.find('div', attrs={'class': 'brdGris2'}).find('h3', attrs={'class': 'titu4'}).find('span').get_text()
        numeros_lineas.append(numero_linea)
    return(numeros_lineas)

def obtener_tipo_transporte(url_lista):
    tipo_transportes = []
    for url in url_lista:
        soup = html(url)
        tipo_transporte_linea = soup.find('div', attrs={'id': 'colCentro'}).find('h2', attrs={'class': 'titu1 metido'}).get_text()
        tipo_transportes.append(tipo_transporte_linea)
    return(tipo_transportes)


#Url de metro, metro ligero y cercanías
url_metro = 'https://www.crtm.es/tu-transporte-publico/metro/lineas.aspx'
url_ml = 'https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas.aspx'
url_cr = 'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas.aspx'


#Llamadas a las funciones
url_lista = obtener_link_lineas(url_metro)
nombres_paradas = obtener_nombre_paradas(url_lista)
orden_paradas = obtener_orden_paradas(url_lista)
numero_lineas = obtener_numero_linea(url_lista)
tipo_transportes = obtener_tipo_transporte(url_lista)


#Preparar las salidas de las funcioneas a listas para el df
nombres_paradas2 = [item for lista in nombres_paradas for item in lista]
orden_paradas2 = [item for lista in orden_paradas for item in lista]

count = 0
numero_lineas2 = []
for numero in numero_lineas:
    numero_lineas2.append([numero]*len(nombres_paradas[count]))
    count += 1
numero_lineas3 = [item for lista in numero_lineas2 for item in lista]

count2 = 0
tipo_transportes2 = []
for tipo in tipo_transportes:
    if 'Cercanías' in tipo:
        tipo = 'CR'
    elif 'Ligero' in tipo:
        tipo = 'ML'
    else:
        tipo = 'METRO'

    tipo_transportes2.append([tipo]*len(nombres_paradas[count2]))
    count2 += 1
tipo_transportes3 = [item for lista in tipo_transportes2 for item in lista]


df_stop_metro = pd.DataFrame({'transportmean_name': tipo_transportes3, 'line_number': numero_lineas3, 'order_number': orden_paradas2, 'stop_name': nombres_paradas2})

print(df_stop_metro)
