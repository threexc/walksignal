#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.utils as utils

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

class DataSet:
    def __init__(self, filename):
        print(filename)
        self.data_file = filename
        self.data_path = self.data_file.rsplit('/', 1)[0]
        self.dataset_name = self.data_path.rsplit('/', 1)[1]
        self.map_path = self.data_path + "/map.png"
        self.bbox_path = self.data_path + "/bbox.txt"
        self.data_matrix = np.array(utils.read_csv(filename))
