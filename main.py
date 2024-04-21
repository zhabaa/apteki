import sys
from argparse import ArgumentParser

from PIL import Image

from yandex_maps import *


def main():
    parser = ArgumentParser()
    parser.add_argument(
        'address',
        help='Адрес без пробелов (Например: Сыктывкар,ул.Коммунистическая,9)'
    )

    args = parser.parse_args()

    long_lat = get_toponym_long_lat(args.address)

    if not long_lat:
        print(f'[!] Error координаты не определены')
        sys.exit(1)

    organizations = get_organizations(long_lat, 'аптека')

    if not organizations:
        print(f'[!] Error аптеки не найдены')
        sys.exit(1)

    points = [format_point(long_lat, r'flag')]

    for organization in organizations:
        if 'TwentyFourHours' in organization.availabilities.keys():
            style = r'pm2gnm'

        elif 'Intervals' in organization.availabilities.keys():
            style = r'pm2blm'

        else:
            style = r'pm2grm'

        points.append(format_point(organization.coordinates, style))

    Image.open(get_map_image(pt=format_points(*points))).show()


if __name__ == '__main__':
    main()
