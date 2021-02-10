#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.utils as utils
from pymongo import MongoClient
from bson.json_util import dumps

class DataBase:
    def __init__(self, filename):
        self.data_file = filename
        self.data_path = self.data_file.rsplit('/', 1)[0]
        self.dataset_name = self.data_path.rsplit('/', 1)[1]
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"
        self.mongo_client = MongoClient()
        self.db = self.mongo_client.towerdata
        self.collection = self.db['towerdata']
        header = [ "num_id", "mcc", "mnc", "lac", "cellid", "lat", "lon", "signal", "measured_at", "rating", "speed", "direction", "act", "ta", "psc", "tac", "pci", "sid", "nid", "bid" ]
        with open(self.data_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                doc={}
                for n in range(0,len(header)-1):
                    if (n == 0):
                        numeric_id = str(row[0]) + str(row[1]) + str(row[2]) + str(row[3])
                        doc[header[n]] = numeric_id
                    else:
                        doc[header[n]] = row[n]

                self.db.towerdata.insert(doc)

        cursor = self.collection.find({})
        with open('collection.json', 'w') as col:
            col.write('[')
            for document in cursor:
                col.write(dumps(document))
                col.write(',')
            col.write(']')

class DataPoint:
    def __init__(self, mcc, mnc, lac, cellid, lat, lon, signal,
            measured_at, rating, speed, direction, access_type,
            timing_advance, tac, pci):
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cellid = cellid
        self.lat = lat
        self.lon = lon
        self.signal = signal
        self.measured_at = measured_at
        self.rating = rating
        self.speed = speed
        self.direction = direction
        self.access_type = access_type
        self.timing_advance = timing_advance
        self.tac = tac
        self.pci = pci
        self.numeric_id = str(self.mcc) + str(self.mnc) + str(self.lac) + str(self.cellid)

class DataSet:
    def __init__(self, filename):
        print(filename)
        self.data_file = filename
        self.data_path = self.data_file.rsplit('/', 1)[0]
        self.dataset_name = self.data_path.rsplit('/', 1)[1]
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"
        self.data_matrix = np.array(utils.read_csv(filename))

        # Determine start and end times of test and get a time range for the trip
        self.time_range = np.array(self.data_matrix[1:,7], dtype=float)
        self.start_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[0]/1000.))
        self.end_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[-1]/1000.))
        self.normalized_time_range = (self.time_range - self.time_range[0])/1000
        self.lat = np.array(self.data_matrix[1:,4], dtype=float)
        self.lon = np.array(self.data_matrix[1:,5], dtype=float)

        # get signal strength in dBm
        self.signal_range = np.array(self.data_matrix[1:,6], dtype=float)

        # get physical cell IDs
        self.pcis = np.array(self.data_matrix[1:,15], dtype=float)

        # get device speed
        self.speed_values = np.array(self.data_matrix[1:,9], dtype=float)
        self.mcc = np.array(self.data_matrix[1:,0], dtype=int)
        self.mnc = np.array(self.data_matrix[1:,1], dtype=int)
        self.cellid = np.array(self.data_matrix[1:,3], dtype=int)
        self.rating = np.array(self.data_matrix[1:,8], dtype=float)
        self.direction = np.array(self.data_matrix[1:,10], dtype=float)
        self.timing_advance = np.array(self.data_matrix[1:,12], dtype=float)

        # get access types and convert them to usable format
        self.access_type_range = np.array(self.data_matrix[1:,11])
        self.access_type_color_codes = np.zeros(len(self.access_type_range), dtype="str")
        for x in range(len(self.access_type_range)):
            if self.access_type_range[x] == "LTE":
                self.access_type_color_codes[x] = "r"
            elif self.access_type_range[x] == "LTE+":
                self.access_type_color_codes[x] = "b"
            elif self.access_type_range[x] == "UMTS":
                self.access_type_color_codes[x] = "g"
            elif self.access_type_range[x] == "HSPA+":
                self.access_type_color_codes[x] = "k"
            else:
                self.access_type_color_codes[x] = "y"
        self.hash = {}
        self.hash['time'] = self.normalized_time_range
        self.hash['signal_strength'] = self.signal_range
        self.hash['pcis'] = self.pcis
        self.hash['speed'] = self.speed_values
        self.hash['mcc'] = self.mcc
        self.hash['mnc'] = self.mnc
        self.hash['cellid'] = self.cellid
        self.hash['rating'] = self.rating
        self.hash['direction'] = self.direction
        self.hash['advance'] = self.timing_advance
