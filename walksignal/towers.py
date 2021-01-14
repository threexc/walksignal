#!/usr/bin/python3 
import csv
import sys
import numpy as np

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

class TowerSet:
    def __init__(self):
        self.tower_id_list = []
        self.tower_list = []
        self.mcc_list = []
        self.mnc_list = []
        self.lac_list = []
        self.cellid_list = []

    def __get_tower_info(self, data_file):
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

    def get_tower_characteristics(self, data_file, reference_file):
        self.__get_tower_info(data_file)
        reference_data = read_csv(reference_file)
        for row in reference_data:
            for entry in self.tower_id_list:
                if ((row[1] == entry[0]) and (row[2] == entry[1]) and (row[3] == entry[2]) and (row[4] == entry[3])):
                    self.tower_list.append(Tower(row[0], row[1], row[2], row[3], row[4], row[6], row[7], row[8], row[9]))
                    
def read_csv(data_file):
    with open(data_file) as csv_file:
        data = list(csv.reader(csv_file, delimiter=","))
        csv_file.close()
    return data

if __name__ == "__main__":
    towerset = TowerSet()
    towerset.get_tower_characteristics(sys.argv[1], sys.argv[2])
    print(towerset.tower_id_list)
    print(towerset.tower_list[0].mcc)
    print(towerset.tower_list[0].mnc)
    print(towerset.tower_list[0].lac)
    print(towerset.tower_list[0].cellid)
    print(towerset.tower_list[0].lat)
    print(towerset.tower_list[0].lon)
    print(towerset.tower_list[0].range)
    print(towerset.tower_list[0].samples)
    print(towerset.tower_list[0].signal_type)

