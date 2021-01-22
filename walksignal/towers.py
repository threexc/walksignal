#!/usr/bin/python3 
import csv
import sys
import numpy as np
import walksignal.utils as utils
import walksignal.data as data

class Tower:
    def __init__(self, signal_type, mcc, mnc, lac, cellid, lon, lat, tower_range, samples):
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cellid = cellid
        self.lat = lat
        self.lon = lon
        self.range = tower_range
        self.samples = samples
        self.signal_type = signal_type

class TowerList:
    def __init__(self, data_file, reference_file):
        self.tower_id_list = []
        self.tower_list = []
        self.mcc_list = []
        self.mnc_list = []
        self.lac_list = []
        self.cellid_list = []

        self.__get_tower_characteristics(data_file, reference_file)

    def __get_tower_info(self, data_file):
        self.data = utils.read_csv(data_file)
        self.data_matrix = np.array(self.data)
        
        for row in self.data_matrix:
            if row[0] not in self.mcc_list:
                self.mcc_list.append(row[0])
                self.mnc_list.append(row[1])
                self.lac_list.append(row[2])
                self.cellid_list.append(row[3])
            elif row[1] not in self.mnc_list:
                self.mnc_list.append(row[1])
                self.lac_list.append(row[2])
                self.cellid_list.append(row[3])
            elif row[2] not in self.lac_list:
                self.lac_list.append(row[2])
                self.cellid_list.append(row[3])
            elif row[3] not in self.cellid_list:
                self.cellid_list.append(row[3])
                self.tower_id_list.append((row[0], row[1], row[2], row[3]))

    def __get_tower_characteristics(self, data_file, reference_file):
        self.__get_tower_info(data_file)
        reference_data = utils.read_csv(reference_file)
        for row in reference_data:
            for entry in self.tower_id_list:
                if ((row[1] == entry[0]) and (row[2] == entry[1]) and (row[3] == entry[2]) and (row[4] == entry[3])):
                    self.tower_list.append(Tower(row[0], row[1], row[2], row[3], row[4], row[6], row[7], row[8], row[9]))

class TowerDataSet:
    def __init__(self, dataset, tower):
        self.points = []
        self.tower = tower

        for row in dataset:
            if ((self.tower.mcc == row[0]) and (self.tower.mnc == row[1]) and (self.tower.lac == row[2]) and (self.tower.cellid == row[3])):
                self.points.append(data.DataPoint(row[0], row[1], row[2],
                    row[3], row[4], row[5], row[6], row[7], row[8],
                    row[9], row[10], row[11], row[12], row[14],
                    row[15]))
