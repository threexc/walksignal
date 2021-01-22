#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import argparse
import requests
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.data as data
import walksignal.plotter as plotter
import walksignal.towers as towers
import walksignal.utils as utils


def combine_data(datafile, reference_file):
    figs = {}
    axs = {}
    signal_data = np.array([])
    tower_list = []
    tower_lat_data = np.array([])
    tower_lon_data = np.array([])
    dataset = None
    plotter = None
    map_bbox = None
    towerset = None

    dataset = data.DataSet(datafile)
    plotter = SignalPlotter(dataset)
    towerlist = towers.TowerList(datafile, reference_file)
    

    for tower in towerlist.tower_list:
        tower_lat_data = np.concatenate([tower_lat_data, [float(tower.lat)]])
        tower_lon_data = np.concatenate([tower_lon_data, [float(tower.lon)]])
    
    lat_data = np.array(dataset.data_matrix[1:,4], dtype=float)
    lon_data = np.array(dataset.data_matrix[1:,5], dtype=float)
    signal_data = np.array(dataset.data_matrix[1:,6], dtype=float)
    print(lat_data)
    print(lon_data)
    plot_map = plt.imread(plotter.plot_map)
    map_bbox = [entry for entry in utils.get_bbox(dataset.bbox_path)[0]]
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.imshow(plot_map, zorder=0, extent = map_bbox, aspect = "equal")
    cm = plt.cm.get_cmap('gist_heat')

    plot = ax1.scatter(lon_data, lat_data, zorder=1, alpha=1.0, c=signal_data, cmap=cm, s=40)
    ax1.scatter(tower_lon_data, tower_lat_data, zorder=1, alpha=1.0, color="blue")
    plt.xlim(map_bbox[0], map_bbox[1])
    plt.ylim(map_bbox[2], map_bbox[3])
    plt.ylabel("Latitude", rotation=90)
    plt.xlabel("Longitude", rotation=0)
    plt.title("Signal Power vs Position")
    ax = plt.axes()

    # Make sure to prevent lat/long from being displayed in scientific
    # notation
    ax.ticklabel_format(useOffset=False)
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cbar = plt.colorbar(plot, cax = cax)
    cbar.ax.set_ylabel("Signal Power (dBm)", rotation=270, labelpad=10)

    plt.show()

def plot_data(x_axis, y_axis, annotation=None, x_label="X", y_label="Y", plot_title="X vs Y"):
    scatter = plt.scatter(x_axis, y_axis, c = annotation, s = 2)
    if annotation is not None:
        for element in range(len(x_axis)):
            if annotation[element] is not None:
                plt.text(x_axis[element], y_axis[element], str(annotation[element]))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid()

    # Make sure that the axes don't display scientific notation. Need a
    # cleaner fix for this
    plt.gcf().axes[0].xaxis.get_major_formatter().set_scientific(False)
    plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)

    lte = mpatches.Patch(color="r", label="LTE")
    lte_plus = mpatches.Patch(color="b", label="LTE+")
    umts = mpatches.Patch(color="g", label="UMTS")
    hspa_plus = mpatches.Patch(color="k", label="HSPA+")
    plt.legend(handles=[lte, lte_plus, umts, hspa_plus])
    plt.suptitle(plot_title)
    plt.show()

class SignalPlotter:
    def __init__(self, dataset):
        self.dataset = dataset
        self.plot_map = self.dataset.data_path + "/map.png"
        self.dataset_name = self.dataset.dataset_name

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
        self.plot = plt.imread(self.plot_map)
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
