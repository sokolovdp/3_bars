#!/usr/bin/python3

import json
import codecs
import chardet
from math import cos, asin, sqrt


def get_encoding(filename: "str") -> "str":  # identify the name of encoding of the given file
    with open(filename, "rb") as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']


def load_data(filename: "str") -> "dict":
    try:
        json_data = json.load(codecs.open(filename, 'r', get_encoding(filename)))
    except IOError:
        print("io error during loading bar's data")
        exit(1)
    except json.decoder.JSONDecodeError:
        print("invalid json format in bar's data")
        exit(2)
    else:
        return json_data


def get_biggest_bar(bars_data: "dict") -> "tuple":
    bars_sits = [(i, bar['SeatsCount']) for i, bar in enumerate(bars_data)]
    index = max(bars_sits, key=lambda t: t[1])[0]
    return bars_data[index], index


def get_smallest_bar(bars_data: "dict") -> "tuple":
    #  we assume that if number of sits is less than 5 its an error in source data of the bar
    bars_sits = [(i, bar['SeatsCount']) for i, bar in enumerate(bars_data) if bar['SeatsCount'] >= 5]
    index = min(bars_sits, key=lambda t: t[1])[0]
    return bars_data[index], index


def haversine_distance(lat1: "float", lon1: "float", lat2: "float", lon2: "float") -> "float":
    # calculates distance in km, using the 'Haversine' formula
    p = 0.017453292519943295  # Pi/180
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))  # 2*Earth Radius*asin...


def get_closest_bar(bars_data: "dict", lat: "float", lon: "float") -> "tuple":
    bars_distances = [(i, haversine_distance(lat, lon, float(bar['Latitude_WGS84']), float(bar['Longitude_WGS84'])))
                      for i, bar in enumerate(bars_data)]
    index = min(bars_distances, key=lambda t: t[1])[0]
    return bars_data[index], index, bars_distances


def main(lat, lon, all_bars_in_moscow):
    closest_bar, closest_bar_id, bars_distances = get_closest_bar(all_bars_in_moscow, lat, lon)
    smallest_bar, smallest_bar_id = get_smallest_bar(all_bars_in_moscow)
    biggest_bar, biggest_bar_id = get_biggest_bar(all_bars_in_moscow)

    print("smallest bar in Moscow  is {} it's {:.2f} kms from your coordinates".format(smallest_bar['Name'],
                                                                                       bars_distances[smallest_bar_id][
                                                                                           1]))

    print("biggest bar in Moscow  is {} it's {:.2f} kms from your coordinates".format(biggest_bar['Name'],
                                                                                      bars_distances[biggest_bar_id][
                                                                                          1]))

    print("closest bar in Moscow  is {} it's {:.2f} kms from your coordinates".format(closest_bar['Name'],
                                                                                      bars_distances[closest_bar_id][
                                                                                          1]))


if __name__ == '__main__':
    moscow_bars_data = load_data('moscow_bars.json')
    lati = float(input("enter latitude  in rad format: "))
    long = float(input("enter longitude in rad format: "))
    main(lati, long, moscow_bars_data)
