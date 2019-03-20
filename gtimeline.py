import os
import csv
import json
import logging
import argparse
from datetime import datetime as dt


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('gtimeline.log')
fh.setLevel(logging.DEBUG)

fformatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
fh.setFormatter(fformatter)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

cformatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(cformatter)

logger.addHandler(fh)
logger.addHandler(ch)


def parse_hist_data(json_file, c_threshold, no_activity):
    '''
    This function will parse the google history json file.

    Args:
        json_file (str): the history json file
        c_threshold (int): the threshold of the confidence for each activity
        no_activity (bool): If True ignore locations without any activity
    '''
    logger.info('Loading json data from {}'.format(json_file))

    with open(json_file, 'r') as fh:
        json_data = json.load(fh)

    for location in json_data['locations']:
        if 'activity' in location:
            loc_time = dt.fromtimestamp(float(location['timestampMs'])/1000).strftime('%c')
            loc_lat = location['latitudeE7'] / 1e7
            loc_long = location['longitudeE7'] / 1e7
            activity_type = 'listed'
            print('Lat:{}, Lon:{}, Activity:{}, Date:{}'.format(loc_lat, loc_long, activity_type, loc_time))
            for activity in location['activity']:
                activity_time = dt.fromtimestamp(float(activity['timestampMs'])/1000).strftime('%c')
                activity_type = activity['activity'][0]['type']
                activity_confidence = activity['activity'][0]['confidence']
                print('\t Activity:{}, Confidence:{}, Date:{}'.format(activity_type, activity_confidence, activity_time)) 
        else:
            if not no_activity:
                loc_time = dt.fromtimestamp(float(location['timestampMs'])/1000).strftime('%c')
                loc_lat = location['latitudeE7'] / 1e7
                loc_long = location['longitudeE7'] / 1e7
                activity_type = 'none'
                print('Lat:{}, Lon:{}, Activity:{}, Date:{}'.format(loc_lat, loc_long, activity_type, loc_time))

    print('Total locations: {}'.format(len(json_data['locations'])))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                        description='''Parse the google timeline json file into
                        a more human read-able csv file.''')
    parser.add_argument('-f', '--file', type=str, action='store', 
                        dest='json_file', required=True, 
                        help='the path to the json file')
    parser.add_argument('-c', '--confidence', type=int, action='store', 
                        dest='c_threshold', default=0, 
                        help='the confidence threshold')
    parser.add_argument('--noactivity', action='store_true', 
                        dest='no_activity', default=False, 
                        help='ignore data locations without activity') 

    results = parser.parse_args()

    parse_hist_data(results.json_file, results.c_threshold, results.no_activity)
