#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

class DataSet:

    def __init__(self, filename):
       self.data_file = filename
       self.data_path = self.data_file.rsplit('/', 1)[0]
       self.dataset_name = self.data_path.rsplit('/', 1)[1]
       self.map_path = self.data_path + "/map.png"
       self.verbose = False

    def read_data(self, data=None):
        if data == None:
            with open(self.data_file) as csv_file:
                self.data = list(csv.reader(csv_file, delimiter=","))
                csv_file.close()
        else:
            self.data = data
        self.data_matrix = np.array(self.data)
        
        # Determine start and end times of test and get a time range for the trip
        self.time_range = np.array(self.data_matrix[1:,7], dtype=float)
        self.start_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[0]/1000.))
        self.end_time = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(self.time_range[-1]/1000.))
        self.normalized_time_range = (self.time_range - self.time_range[0])/1000
        self.spatial_lat = np.array(self.data_matrix[1:,4], dtype=float)
        self.spatial_lon = np.array(self.data_matrix[1:,5], dtype=float)

        # hard-code the box properties for the map, since it'll be the
        # same one every time
        self.map_bbox = (-75.70629, -75.69213, 45.41321, 45.41976)
        
        # get signal strength in dBm
        self.signal_range = np.array(self.data_matrix[1:,6], dtype=float)

        # get physical cell IDs
        self.pcis = np.array(self.data_matrix[1:,15], dtype=float)

        # get device speed
        self.speed_values = np.array(self.data_matrix[1:,9], dtype=float)

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

        if self.verbose is True:
            print(self.start_time)
            print(self.end_time)
            print(self.normalized_time_range)
            print(self.signal_range)
            print(self.pcis)
            print(self.speed_values)
            print(self.access_type_color_codes)
            print(self.access_type_range)

class SignalPlotter:

    def __init__(self, dataset):
        self.dataset = dataset
        self.time_range = self.dataset.normalized_time_range
        self.signal_range = self.dataset.signal_range
        self.access_types = self.dataset.access_type_range
        self.access_type_color_codes = self.dataset.access_type_color_codes
        self.pcis = self.dataset.pcis
        self.speed_values = self.dataset.speed_values
        self.map_file = self.dataset.data_path + "/map.png"
        self.dataset_name = self.dataset.dataset_name
        self.map_bbox = self.dataset.map_bbox
        self.spatial_lat = self.dataset.spatial_lat
        self.spatial_lon = self.dataset.spatial_lon

    def plot_dbm_and_speed(self, independent, dependent, annotation = None):
        plt.subplot(2,1,1)
        plt.scatter(independent, dependent, c=self.access_type_color_codes)
        for element in range(len(self.time_range)):
            if annotation is not None:
                plt.text(independent[element], dependent[element], str(annotation[element]))
        plt.xlabel("Time (seconds)")
        plt.ylabel("Signal Strength (dBm)")
        plt.grid()
        lte = mpatches.Patch(color="r", label="LTE")
        lte_plus = mpatches.Patch(color="b", label="LTE+")
        umts = mpatches.Patch(color="g", label="UMTS")
        hspa_plus = mpatches.Patch(color="k", label="HSPA+")
        plt.legend(handles=[lte, lte_plus, umts, hspa_plus])
        plt.suptitle("Mixed LTE/LTE+/UMTS/HSPA Signal Strength Over Time, Start Time {0} UTC".format(self.dataset.start_time))

        plt.subplot(2,1,2)
        plt.plot(self.time_range, self.speed_values, 'o--')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Speed (m/s)")
        plt.grid()

        plt.show()
    
    def plot_dbm_vs_time(self, independent, dependent, annotation=None):
        self.scatter = plt.scatter(independent, dependent, c=self.access_type_color_codes)
        for element in range(len(self.time_range)):
            if annotation is not None:
                plt.text(independent[element], dependent[element], str(annotation[element]))
        plt.xlabel("Time (seconds)")
        plt.ylabel("Signal Strength (dBm)")
        plt.grid()
        lte = mpatches.Patch(color="r", label="LTE")
        lte_plus = mpatches.Patch(color="b", label="LTE+")
        umts = mpatches.Patch(color="g", label="UMTS")
        hspa_plus = mpatches.Patch(color="k", label="HSPA+")
        plt.legend(handles=[lte, lte_plus, umts, hspa_plus])
        plt.suptitle("Mixed LTE/LTE+/UMTS/HSPA Signal Strength Over Time, Start Time {0} UTC".format(self.dataset.start_time))
        plt.show()
    
    def plot_speed_vs_time(self, annotation=None):
        self.plot = plt.plot(self.time_range, self.speed_values, 'o--')
        for element in range(len(self.time_range)):
            if annotation is not None:
                plt.text(self.time_range[element], self.speed_values[element], str(annotation[element]))
        plt.xlabel("Time (seconds)")
        plt.ylabel("Speed (m/s)")
        plt.grid()
        lte = mpatches.Patch(color="r", label="LTE")
        lte_plus = mpatches.Patch(color="b", label="LTE+")
        umts = mpatches.Patch(color="g", label="UMTS")
        hspa_plus = mpatches.Patch(color="k", label="HSPA+")
        plt.legend(handles=[lte, lte_plus, umts, hspa_plus])
        plt.suptitle("Mixed LTE/LTE+/UMTS/HSPA Device Speed Over Time, Start Time {0} UTC".format(self.dataset.start_time))
        plt.show()
    
    def plot_path(self):
        self.plot = plt.imread(self.map_file)
        fig, ax = plt.subplots(figsize = (8,7))
        mainplot = ax.scatter(self.spatial_lon, self.spatial_lat, zorder=1,
                alpha=1.0, c=self.dataset.signal_range, cmap='gist_heat', s=40)
        ax.set_title(self.dataset_name)
        ax.set_xlim(self.map_bbox[0], self.map_bbox[1])
        ax.set_ylim(self.map_bbox[2], self.map_bbox[3])
        im = ax.imshow(self.plot, zorder=0, extent = self.map_bbox, aspect= 'equal')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="2.5%", pad=0.05)
        plt.colorbar(mainplot, cax=cax)
        plt.show()
