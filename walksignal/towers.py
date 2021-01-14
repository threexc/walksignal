#!/usr/bin/python3 
import csv
import sys
import numpy as np

class Tower:
    def __init__(self, mcc, mnc, lac, cellid):
        self.lat = lat
        self.lon = lon
        self.range = tower_range
        self.samples = samples
        self.type = signal_type

class TowerSet:
    def __init__(self):
        self.tower_id_list = []
        self.tower_list = []
        self.mcc_list = []
        self.mnc_list = []
        self.lac_list = []
        self.cellid_list = []

    def get_tower_info(self, data_file):
        self.data = read_csv(data_file)
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
                
def read_csv(data_file):
    with open(data_file) as csv_file:
        data = list(csv.reader(csv_file, delimiter=","))
        csv_file.close()
    return data

if __name__ == "__main__":
    towerset = TowerSet()
    towerset.get_tower_info(sys.argv[1])
    print(towerset.tower_id_list)

