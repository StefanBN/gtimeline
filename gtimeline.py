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


def translate_hist_data(json_file, out_file, no_activity):
    '''
    This function will parse the google history json file and output the
    data in a human-readable format.

    Args:
        json_file (str): the history json file
        out_file (str): the output file where the parsed data is written
        no_activity (bool): If True add locations without any activity
    '''
    header = ['Date', 'Latitude', 'Longitude', 'Activity', 'Confidence']
    
    if not os.path.isfile(json_file):
        logger.debug('The file {} does not exist!'.format(json_file))
        sys.exit(1)

    logger.info('Loading json data from {}'.format(json_file))
    with open(json_file, 'rb') as fh:
        json_data = json.load(fh)

    logger.info('Total locations: {}'.format(len(json_data['locations'])))
    
    with open(out_file, 'wb') as csvfile:
        csv_write = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_write.writerow(header)

        logger.info('Starting to go through location data...')
        for location in json_data['locations']:
            loc_time = dt.fromtimestamp(
                        float(location['timestampMs'])/1000).strftime('%c')
            loc_lat = location['latitudeE7'] / 1e7
            loc_lon = location['longitudeE7'] / 1e7

            if 'activity' in location:
                for activity in location['activity']:
                    activity_time = dt.fromtimestamp(float(activity['timestampMs'])/1000).strftime('%c')
                    activity_sorted = sorted(activity['activity'],
                                             key=lambda x: x['confidence'],
                                             reverse=True)
                    # todo: add support to collect multiple activities
                    #       based on confidence filter
                    activity_type = activity_sorted[0]['type']
                    activity_confidence = activity_sorted[0]['confidence']
            else:
                if not no_activity:
                    continue
                activity_type = 'none'
                activity_confidence = 0

            csv_write.writerow((loc_time, loc_lat, loc_lon,
                                activity_type, activity_confidence))
        logger.info('Finished processing location data...')


def summary_hist_data(json_file, out_file):
    '''
    This function will parse the google history json file and
    process only data points with an activity. The resulting file
    will have information related to total traveled time per activity.

    Args:
        json_file (str): the history json file
        out_file (str): the output file where the parsed data is written
    '''
    header = ['Latitude', 'Longitude', 'Activity', 'Confidence', 'Date']

    if not os.path.isfile(json_file):
        logger.debug('The file {} does not exist!'.format(json_file))
        sys.exit(1)

    logger.info('Loading json data from {}'.format(json_file))
    with open(json_file, 'rb') as fh:
        json_data = json.load(fh)

    with open(out_file, 'wb') as csvfile:
        csv_write = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_write.writerow(header)

    ###TODO: to be continued

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

    # parser.add_argument('-c', '--confidence', type=int, action='store',
    #                     dest='confidence_level', default=100,
    #                     help='the confidence threshold')

    parser.add_argument('--noactivity', action='store_true',
                        dest='no_activity', default=False,
                        help='add data locations without any activity information')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-t', '--translate', action='store_true',
                        dest='json_translate', default=True,
                        help='translate the json data into a more\
                             human-readable format')

    group.add_argument('-s', '--summary', action='store_true',
                        dest='json_summary', default=False,
                        help='output the data in a specific format')

    results = parser.parse_args()
   
    msg = 'Collecting only locations that have an activity!'
    if results.no_activity:
        msg = 'Collecting all locations, including those without an activity!'

    logger.info(
        'Starting to parse json data from file: {}'.format(results.json_file))
    logger.info(msg)

    if results.json_summary:
        summary_hist_data(results.json_file, results.out_file)

    if results.json_translate:
        translate_hist_data(results.json_file, results.out_file, results.no_activity)
