import scrapper_crtm as crtm
import pandas as pd
import string
import unidecode
from typing import List, Dict, Tuple

TRANSPORT_TYPES = ["metro", "metro-ligero", "cercanias-renfe"]


def clean_station(station: str) -> str:
    """
    Function that cleans a station name.
    :param station: stop name
    :return: clean stop name
    """
    # Accents
    new_station = unidecode.unidecode(station)
    # Uppercase
    new_station = new_station.upper()
    # Stations with (ida), (vuelta)
    new_station = new_station.split('(')[0]
    # Unnecessary spaces
    new_station = new_station.strip()
    # Other processes
    new_station = new_station.replace('RDA.', 'RONDA')
    new_station = new_station.replace('AVDA.', 'AVENIDA')
    new_station = new_station.replace("'", '')
    new_station = new_station.replace(" - ", '-')

    if new_station == 'MOSTOLES-EL SOTO':
        new_station = 'MOSTOLES EL SOTO'
    elif new_station == 'BARRIAL-C.COM.POZUELO EL':
        new_station = 'EL BARRIAL-C.C. POZUELO'
    elif new_station == 'PUERTO NAVACERRADA':
        new_station = 'PUERTO DE NAVACERRADA'
    elif new_station == 'ATOCHA RENFE':
        new_station = 'ATOCHA-RENFE'
    elif new_station == 'AEROPUERTO T1 T2 T3':
        new_station = 'AEROPUERTO T1-T2-T3'
    return new_station


def from_dict_to_list(stations_dict: Dict) -> List[Tuple]:
    """
    Converts the dictionary from the scraper into a list of tuples.
    :param stations_dict: stations obtained from the web.
    :return: list of tuples (transport, station, line, order_line)
    """
    stations_list = []
    for t in TRANSPORT_TYPES:
        for line, stations in stations_dict[t].items():
            for s in stations:
                stations_list.append((t, s, line,
                                      line + '_' + str(stations.index(s) + 1)))
    return stations_list


def clean_df(pd_df: pd.DataFrame, web: bool = True) -> pd.DataFrame:
    """
    Function that cleans a data frame.
    :param pd_df:
    :param web: there are 2 sources: web and stops.
    :return:
    """
    if web:
        pd_df['line_number'] = pd_df['line_number']\
            .apply(lambda x: x.replace('-', ''))
        pd_df['order_number'] = pd_df['order_number']\
            .apply(lambda x: x.replace('-', ''))
    pd_df['stop_name'] = pd_df['stop_name'].apply(clean_station)
    return pd_df


def web_df(stations: Dict) -> pd.DataFrame:
    """
    Function that processes and cleans the dictionary generated by the scraper.
    :param stations: stations obtained from the web.
    :return: data frame containing structured information for the web stations.
    """
    stations_list = from_dict_to_list(stations)
    # Create Pandas df
    pd_stations = pd.DataFrame(stations_list, columns=['transportmean_name',
                                                       'stop_name',
                                                       'line_number',
                                                       'order_number'])
    # Cleaning
    pd_stations = clean_df(pd_stations)
    return pd_stations


def stops_transport_df(transport: str) -> pd.DataFrame:
    """
    Function that processes and cleans a stop.txt file for a transport
    :param transport: indicates the transport
    :return: data frame containing structured information for a stops.txt file.
    """
    pd_stops = pd.read_csv("stops-{}.txt".format(transport))
    # Cleaning
    pd_stops = clean_df(pd_stops, web=False)
    # Only stops
    pd_stops_par = pd_stops[pd_stops.location_type == 0].copy()
    # Process cercanias
    if transport == "cercanias-renfe":
        pd_stops_par['stop_name'] = pd_stops_par['stop_name']\
            .apply(lambda x: x.split()[-1] + ' ' + ' '.join(
                   x.split()[:-1]) if x.split()[-1] in ['EL', 'LA', 'LAS', 'LOS']
                   else x)
    # Get the first stop for each stop name in stops.txt
    pd_stops_group = pd_stops_par.groupby('stop_name').first()
    return pd_stops_group


def join_web_stops() -> pd.DataFrame:
    """
    Function that executes the scraper, loads the stops.txt files, cleans and
    process each source and joins the information.
    :return: a data frame with the information of both sources.
    """
    # Info from scrapper
    stations_web = crtm.get_all_stations()
    # Convert to pandas data frame
    pd_stations_web = web_df(stations_web)
    # Join info for all transports
    stops_info = None
    for t in TRANSPORT_TYPES:
        # Web info for a transport
        stations_t = pd_stations_web[pd_stations_web.transportmean_name == t]
        # Stops info for a transport
        stops_t = stops_transport_df(t)
        # Join info
        pd_join = stations_t.merge(stops_t.reset_index(),
                                   on=['stop_name'], how='left')
        if stops_info is None:
            stops_info = pd_join
        else:
            stops_info = pd.concat([stops_info, pd_join])
    return stops_info


def save_stops_csv(pd_df: pd.DataFrame):
    """
    Saves the final data frame to csv.
    :param pd_df: data frame with information of both sources.
    """
    pd_df['transportmean_name'] = pd_df['transportmean_name'] \
        .apply(lambda x: 'METRO' if x == 'metro'
               else ('ML' if x == 'metro-ligero' else 'CR'))
    columns = ['transportmean_name', 'line_number', 'order_number', 'stop_id',
               'stop_code', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon',
               'zone_id', 'stop_url', 'location_type', 'parent_station',
               'stop_timezone', 'wheelchair_boarding']
    pd_df = pd_df.loc[:, columns]
    pd_df.to_csv("stops_web.csv", index=False)


if __name__ == '__main__':
    # Loads info from scraper and stops.txt, and joins it
    pd_stops_info = join_web_stops()
    # Save as csv
    save_stops_csv(pd_stops_info)
