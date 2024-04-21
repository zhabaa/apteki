import json
from io import BytesIO
from math import radians, cos, sin, atan2, ceil

import requests

_MAP_API_SERVER = 'http://static-maps.yandex.ru/1.x/'

_GEOCODER_API_SERVER = 'http://geocode-maps.yandex.ru/1.x/'
_GEOCODER_API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'

_SEARCH_API_SERVER = 'https://search-maps.yandex.ru/v1/'
_SEARCH_API_KEY = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'

_EARTH_RADIUS = 6_372_795


def get_toponym_long_lat(address):
    geocoder_params = {
        'apikey': _GEOCODER_API_KEY,
        'geocode': address,
        'results': 1,
        'format': 'json'
    }

    response = requests.get(url=_GEOCODER_API_SERVER, params=geocoder_params)

    if not response:
        return None

    json_response = response.json()
    geo_object = json_response[
        'response'][
        'GeoObjectCollection'][
        'featureMember'][0][
        'GeoObject']

    return geo_object['Point']['pos'].split(' ')


def get_toponym_by_long_lat(long_lat, **kwargs):
    geocoder_params = {
        'apikey': _GEOCODER_API_KEY,
        'geocode': ','.join(long_lat),
        'results': 1,
        'format': 'json'
    }
    geocoder_params.update(kwargs)

    response = requests.get(url=_GEOCODER_API_SERVER, params=geocoder_params)

    if not response:
        return None

    json_response = response.json()
    return json_response[
        'response'][
        'GeoObjectCollection'][
        'featureMember'][0][
        'GeoObject'][
        'metaDataProperty'][
        'GeocoderMetaData'][
        'text']


def get_toponym_spn(address):
    geocoder_params = {
        'apikey': _GEOCODER_API_KEY,
        'geocode': address,
        'results': 1,
        'format': 'json'
    }

    response = requests.get(url=_GEOCODER_API_SERVER, params=geocoder_params)

    if not response:
        return None

    json_response = response.json()
    bbox = json_response[
        'response'][
        'GeoObjectCollection'][
        'featureMember'][0][
        'GeoObject'][
        'boundedBy'][
        'Envelope']

    return ','.join((str(u - l) for u, l in zip(
        (s for s in bbox['upperCorner'].split(' ')),
        (s for s in bbox['lowerCorner'].split(' '))))
                    )


class Organization:
    def __init__(self, name: str, address: str, availabilities: str, coordinates: list[float]):
        self.name = name
        self.address = address
        self.availabilities = availabilities
        self.coordinates = coordinates


def get_organizations(long_lat, text='', **kwargs):
    search_params = {
        'apikey': _SEARCH_API_KEY,
        'text': text,
        'lang': 'ru_RU',
        'results': 10,
        'll': ','.join(long_lat),
        'type': 'biz'
    }
    search_params.update(kwargs)

    response = requests.get(url=_SEARCH_API_SERVER, params=search_params)

    if not response:
        return None

    json_response = response.json()
    organizations = list()

    # get_json_file('organisations', json_response)

    for organization in json_response['features'][:search_params['results']]:
        organizations.append(Organization(
            organization['properties']['CompanyMetaData']['name'],
            organization['properties']['CompanyMetaData']['address'],
            organization['properties']['CompanyMetaData']['Hours']['Availabilities'][0],
            organization['geometry']['coordinates'])
        )

    return organizations


def format_point(long_lat, style):
    return ','.join(map(str, [long_lat[0], long_lat[1], style]))


def format_points(*points):
    return '~'.join(points)


def get_map_image(long_lat=(), **kwargs):
    map_params = {
        'l': 'map'
    }

    if long_lat:
        map_params['ll'] = ','.join(long_lat)

    map_params.update(kwargs)

    if not (('ll' in map_params) or ('pt' in map_params)):
        return ''

    response = requests.get(url=_MAP_API_SERVER, params=map_params)

    if not response:
        return ''

    return BytesIO(response.content)


def calculate_distance(long_lat_a, long_lat_b):
    long1 = radians(long_lat_a[0])
    long2 = radians(long_lat_b[0])
    lat1 = radians(long_lat_a[1])
    lat2 = radians(long_lat_b[1])

    cl1 = cos(lat1)
    cl2 = cos(lat2)
    sl1 = sin(lat1)
    sl2 = sin(lat2)

    delta = long2 - long1

    c_delta = cos(delta)
    s_delta = sin(delta)

    y = (pow(cl2 * s_delta, 2) ** 0.5 + pow(cl1 * sl2 - sl1 * cl2 * c_delta, 2))
    x = sl1 * sl2 + cl1 * cl2 * c_delta

    return ceil(atan2(y, x) * _EARTH_RADIUS)


def get_json_file(name, response):
    try:
        with open(f'{name}.json', 'w', encoding='utf-8') as file:
            json.dump(response, file, ensure_ascii=False)

        return True

    except Exception as ex:
        return ex
