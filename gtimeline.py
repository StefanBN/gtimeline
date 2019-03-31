import os
import sys
import csv
import json
import logging
import argparse
from datetime import datetime as dt

import pdb

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


def parse_hist_data(json_file, out_file, c_threshold, no_activity):
    '''
    This function will parse the google history json file.

    Args:
        json_file (str): the history json file
        out_file (str): the output file where the parsed data is written
        c_threshold (int): the threshold of the confidence for each activity
        no_activity (bool): If True add locations without any activity
    '''
    header = ['Latitude', 'Longitude', 'Activity', 'Confidence', 'Date']
    
    if not os.path.isfile(json_file):
        logger.debug('The file {} does not exist!'.format(json_file))
        sys.exit(1)

    logger.info('Loading json data from {}'.format(json_file))
    with open(json_file, 'r') as fh:
        json_data = json.load(fh)

    logger.info('Total locations: {}'.format(len(json_data['locations'])))
    
    with open(out_file, 'w') as csvfile:
        csv_write = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_write.writerow(header)

        logger.info('Starting to go through location data...')
        for location in json_data['locations']:
            if 'activity' in location:
                loc_time = dt.fromtimestamp(float(location['timestampMs'])/1000).strftime('%c')
                loc_lat = location['latitudeE7'] / 1e7
                loc_lon = location['longitudeE7'] / 1e7
                for activity in location['activity']:
                    activity_time = dt.fromtimestamp(float(activity['timestampMs'])/1000).strftime('%c')
                    activity_sorted = sorted(activity['activity'], key=lambda x: x['confidence'], reverse=True)
                    # todo: add support to collect multiple activities based on confidence filter
                    activity_type = activity_sorted[0]['type']
                    activity_confidence = activity_sorted[0]['confidence']
                    #print('Lat:{}, Lon:{}, Activity:{}, Confidence:{}, Date:{}'.format(loc_lat, loc_lon, activity_type,
                    #                                                                   activity_confidence, activity_time)) 
                    csv_write.writerow((loc_lat, loc_lon, activity_type, activity_confidence, activity_time))
            else:
                if no_activity:
                    loc_time = dt.fromtimestamp(float(location['timestampMs'])/1000).strftime('%c')
                    loc_lat = location['latitudeE7'] / 1e7
                    loc_lon = location['longitudeE7'] / 1e7
                    activity_type = 'none'
                    activity_confidence = 0
                    #print('Lat:{}, Lon:{}, Activity:{}, Confidence:{}, Date:{}'.format(loc_lat, loc_lon, activity_type, '0', loc_time))
                    csv_write.writerow((loc_lat, loc_lon, activity_type, activity_confidence, loc_time))
        logger.info('Finished processing location data...')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                        description='''Parse the google timeline json file into
                        a more human read-able csv file.''')

    parser.add_argument('-f', '--file', type=str, action='store', 
                        dest='json_file', required=True, 
                        help='the path to the json file')

    parser.add_argument('-o', '--output', type=str, action='store', 
                        dest='out_file', required=True, 
                        help='the path to the output file')

    parser.add_argument('-c', '--confidence', type=int, action='store', 
                        dest='c_threshold', default=100, 
                        help='the confidence threshold')

    parser.add_argument('--noactivity', action='store_true', 
                        dest='no_activity', default=False, 
                        help='ignore data locations without activity') 

    results = parser.parse_args()
   
    msg = 'Collecting only locations that have an activity!'
    if results.no_activity:
        msg = 'Collecting all locations, including those without an activity!'

    logger.info(msg)
    logger.info('Starting to parse json data from file: {}'.format(results.json_file))

    parse_hist_data(results.json_file, results.out_file, results.c_threshold, results.no_activity)

