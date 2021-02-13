#!/usr/bin/python3 
import csv
import sys
import numpy as np
import walksignal.utils as utils

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
        self.data_points = []
        self.distances = []
        self.signal_power = []

class TowerList:
    def __init__(self, data, reference_file):
        self.tower_id_list = []
        self.tower_list = []
        self.cellid_list = []
        self.data = np.array(data)
        self.lats = np.array([])
        self.lons = np.array([])
        
        self.reference_data = utils.read_csv(reference_file)

        # Fill tower_id_list with tuples of mcc, mnc, lac, cellid
        self.get_tower_ids()

        # Add detected towers to the tower_list by comparing mcc, mnc,
        # lac, cellid with the reference file
        self.get_towers()

        # Add all relevant datapoints to each tower's data_points list
        self.get_tower_data_points()
        self.get_distances()
        self.get_power()
        self.get_tower_lats()
        self.get_tower_lons()

    def get_tower_ids(self):
        for row in self.data:
            if row[3] not in self.cellid_list:
                self.cellid_list.append(row[3])
                self.tower_id_list.append((row[0], row[1], row[2], row[3]))

    def get_towers(self):
        for row in self.reference_data:
            for entry in self.tower_id_list:
                if ((row[1] == entry[0]) and (row[2] == entry[1]) and (row[3] == entry[2]) and (row[4] == entry[3])):
                    self.tower_list.append(Tower(row[0], row[1], row[2], row[3], row[4], row[6], row[7], row[8], row[9]))
        
    def get_tower_data_points(self):
        for tower in self.tower_list:
            for row in self.data:
                if ((tower.mcc == row[0]) and (tower.mnc == row[1]) and (tower.lac == row[2]) and (tower.cellid == row[3])):
                    tower.data_points.append(TowerDataPoint(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[14], row[15]))
    
    def get_distances(self):
        for tower in self.tower_list:
            for datapoint in tower.data_points:
                tower.distances.append(utils.get_distance(tower.lat, tower.lon, datapoint.lat, datapoint.lon) * 1000)

    def get_power(self):
        for tower in self.tower_list:
            for datapoint in tower.data_points:
                tower.signal_power.append(float(datapoint.signal))

    def get_tower_lats(self):
        for tower in self.tower_list:
            self.lats = np.concatenate([self.lats, [float(tower.lat)]])

    def get_tower_lons(self):
        for tower in self.tower_list:
            self.lons = np.concatenate([self.lons, [float(tower.lon)]])

    def get_tower_data(self, mcc, mnc, lac, cellid):
        for tower in self.tower_list:
            if ((tower.mcc == mcc) and (tower.mnc == mnc) and (tower.lac == lac) and (tower.cellid == cellid)):
                return tower


class TowerDataPoint:
	def __init__(self, mcc, mnc, lac, cellid, lat, lon, signal, measured_at, rating, speed, direction, access_type, timing_advance, tac, pci):
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

