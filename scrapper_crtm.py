import requests
from bs4 import BeautifulSoup
import re

CRTM_BASE_URL = "http://www.crtm.es"
CRTM_INI_URL = "/tu-transporte-publico.aspx"
TRANSPORT_TYPES = ["metro", "metro-ligero", "cercanias-renfe"]


def get_lines_page_link(transport):
    """
    Function that searches the line link for a given transport.
    :param transport: string. One of {metro, metro-ligero, cercanias-renfe}
    :return: string containing the line link.
    """
    print("Accessing: " + CRTM_BASE_URL + CRTM_INI_URL)
    html = requests.get(CRTM_BASE_URL + CRTM_INI_URL)
    bs_obj = BeautifulSoup(html.text, "html.parser")
    return bs_obj.find("a",
                       href=re.compile("^/tu-transporte-publico/{}/lineas.aspx$"
                                       .format(transport)))


def get_lines_links(lines_page_link, transport):
    """
    Function that searches each line's url for a given transport.
    :param lines_page_link: string containing the line link of a
    transport.
    :param transport: string. One of {metro, metro-ligero, cercanias-renfe}
    :return: string containing each line's url.
    """
    print("Accessing: " + CRTM_BASE_URL + lines_page_link.attrs["href"])
    html = requests.get(CRTM_BASE_URL + lines_page_link.attrs["href"])
    bs_obj = BeautifulSoup(html.text, "html.parser")
    return bs_obj.findAll("a",
                          href=re.compile("^(/tu-transporte-publico/" +
                                          transport +
                                          "/lineas)(/[0-9]{1,2}.*)" +
                                          "(.aspx)$"))


def get_ordered_stations(lines_links):
    """
    Function that searches all of the stations in each of the passed urls for a
    transport.
    :param lines_links: list containing a url for each line of a transport.
    :return: dict containing for each line a list of ordered stations.
    """
    lines_dict = {}
    for line in lines_links:
        print("Accessing: " + CRTM_BASE_URL + line.attrs['href'])
        html = requests.get(CRTM_BASE_URL + line.attrs['href'])
        bs_obj = BeautifulSoup(html.text, "html.parser")
        # Line number
        line_number = bs_obj.find("h4", {"class": "titu4"})\
                            .find("span")\
                            .get_text()
        # Stations
        table = bs_obj.find("table", {"class": "tablaParadas"})
        line_stations = [row.find("a").get_text().strip()
                         for row in table.tbody.find_all("tr")]
        lines_dict[line_number] = line_stations
    return lines_dict


def get_all_stations():
    """
    Function that returns a dictionary where the keys are each of the transports
    and the values are dictionaries containing a list of ordered stations for
    each line.
    :return: dict.
    """
    transport_dict = {}
    for t_type in TRANSPORT_TYPES:
        lines_page_link = get_lines_page_link(t_type)
        lines_links = get_lines_links(lines_page_link, t_type)
        lines_dict = get_ordered_stations(lines_links)
        transport_dict[t_type] = lines_dict
    return transport_dict


if __name__ == '__main__':
    transport_lines_stations = get_all_stations()
    print(transport_lines_stations)











