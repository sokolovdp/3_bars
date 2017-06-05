import json
import sys
import chardet
import os
from math import cos, asin, sqrt, hypot


def load_raw_data_and_encoding_name(filename: "str") -> "tuple":
    with open(filename, "rb") as file:
        raw_data = file.read()
    return raw_data, chardet.detect(raw_data)['encoding']


def load_json_data(filename: "str") -> "dict":
    raw_data, encoding = load_raw_data_and_encoding_name(filename)
    decoded_data = raw_data.decode(encoding)
    try:
        json_data = json.loads(decoded_data)
    except json.decoder.JSONDecodeError:
        print("file {} contains invalid json data, load aborted!".format(filename))
        exit(1)
    else:
        return json_data


def get_biggest_bar(bars_data: "dict") -> "tuple":
    bars_sits = [(bar_id, bar['SeatsCount']) for bar_id, bar in enumerate(bars_data)]
    bar_id = max(bars_sits, key=lambda bar_data: bar_data[1])[0]
    return bars_data[bar_id], bar_id


def get_smallest_bar(bars_data: "dict") -> "tuple":
    #  we assume that if number of sits is less than 5 its an error in source data of the bar
    bars_sits = [(bar_id, bar['SeatsCount']) for bar_id, bar in enumerate(bars_data) if bar['SeatsCount'] >= 5]
    bar_id = min(bars_sits, key=lambda bar_data: bar_data[1])[0]
    return bars_data[bar_id], bar_id


def haversine_distance(lat1: "float", lon1: "float", lat2: "float", lon2: "float") -> "float":
    # calculates distance in km, using the optimized 'Haversine' formula
    p = 0.017453292519943295  # Pi/180
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))  # 2*Earth Radius*asin...


def euclidean_distance(lat1: "float", lon1: "float", lat2: "float", lon2: "float") -> "float":
    # calculates distance in km, using the Euclidean distance formula
    return hypot(lat1 - lat2, lon1 - lon2) * 100


def get_closest_bar(bars_data: "dict", lat: "float", lon: "float") -> "tuple":
    bars_distances = [
        (bar_id, euclidean_distance(lat, lon, float(bar['Latitude_WGS84']), float(bar['Longitude_WGS84'])))
        for bar_id, bar in enumerate(bars_data)]
    bar_id = min(bars_distances, key=lambda bar_data: bar_data[1])[0]
    return bars_data[bar_id], bar_id, bars_distances


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
    if os.path.isfile(sys.argv[1:][0]):
        latitude = float(input("enter latitude  in rad format: "))
        longitude = float(input("enter longitude in rad format: "))
        main(latitude, longitude, load_json_data(sys.argv[1:][0]))
    else:
        print("invalid path or file name: {}".format(sys.argv[1:][0]))
