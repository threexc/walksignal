#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import utm
import math
import argparse
import requests
import geopy
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.data as data
import walksignal.plottools as plottools
import walksignal.towers as towers
import walksignal.utils as utils

class PlotSetup:
    def __init__(self, datafile, reference_file):
        self.tower_list = towers.TowerList(datafile, reference_file)
        self.tower_lat_data = np.array([])
        self.tower_lon_data = np.array([])
        self.__get_tower_positions(self.tower_list.tower_list)
        self.dataset = data.DataSet(datafile)
        self.lat_data = self.dataset.lat
        self.lon_data = self.dataset.lon
        self.signal_data = self.dataset.signal_range
        self.rating = self.dataset.rating
        self.speed_values = self.dataset.speed_values
        self.direction = self.dataset.direction
        self.plot_map = None
        self.map_bbox = None
        self.__get_map_and_bbox()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.__set_image()
        self.cm = plt.cm.get_cmap('gist_heat')
        self.cm2 = plt.cm.get_cmap('gist_gray')
        self.avg_lat_diff = np.average(np.ediff1d(self.lat_data))
        self.avg_lon_diff = np.average(np.ediff1d(self.lon_data))

    def __get_tower_positions(self, tower_list):
        for tower in tower_list:
            self.tower_lat_data = np.concatenate([self.tower_lat_data, [float(tower.lat)]])
            self.tower_lon_data = np.concatenate([self.tower_lon_data, [float(tower.lon)]])

    def __get_map_and_bbox(self):
        self.plot_map = plt.imread(self.dataset.map_path)
        self.map_bbox = [entry for entry in utils.get_bbox(self.dataset.bbox_path)]

    def __set_image(self):
        self.ax1.imshow(self.plot_map, zorder=0, extent = self.map_bbox[0], aspect="equal")

def plot_gsp(datafile, reference_file):
    setup = PlotSetup(datafile, reference_file)

    signals = __plt_signal_scatter(setup.ax1, setup.lon_data, setup.lat_data, setup.signal_data, setup.cm)
    tower_plot = __plt_points_scatter(setup.ax1, setup.tower_lon_data, setup.tower_lat_data, "blue")
    __plt_set_bbox(plt, setup.map_bbox)
    __plt_set_label()
    __plt_set_colorbar(setup, signals)

    plt.show()

def plot_rating(datafile, reference_file):
    setup = PlotSetup(datafile, reference_file)
    #np.set_printoptions(threshold=sys.maxsize)

    signals = __plt_signal_scatter(setup.ax1, setup.lon_data, setup.lat_data, setup.rating, setup.cm)
    tower_plot = __plt_points_scatter(setup.ax1, setup.tower_lon_data, setup.tower_lat_data, "blue")
    __plt_set_bbox(plt, setup.map_bbox)
    __plt_set_label(title="Rating vs Position")
    __plt_set_colorbar(setup, signals, "Rating (m)")
    
    plt.show()

def plot_data(x_axis, y_axis, annotation=None, x_label="X", y_label="Y", plot_title="X vs Y"):
    scatter = __plt_points_scatter(x_axis, y_axis, c = annotation, s = 2)
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

def plot_positioning(datafile, reference_file):
    setup = PlotSetup(datafile, reference_file)
    corrected_lat = []
    corrected_lon = []

    for entry in range(len(setup.lat_data)):
        corrected_lat.append(setup.lat_data[entry])
        corrected_lon.append(setup.lon_data[entry])
    for entry in range(len(setup.lat_data) - 1):
        corr = 1.01
        proj_lat, proj_lon = __project_next_position(setup.lat_data[entry], setup.lon_data[entry], setup.speed_values[entry], setup.direction[entry])
        proj_diff_lat = np.absolute(setup.lat_data[entry] - proj_lat)
        proj_diff_lon = np.absolute(setup.lon_data[entry] - proj_lon)
        orig_diff_lat = np.absolute(setup.lat_data[entry] - setup.lat_data[entry+1])
        orig_diff_lon = np.absolute(setup.lon_data[entry] - setup.lon_data[entry+1])

        if ((orig_diff_lat > proj_diff_lat * corr) and (orig_diff_lon > proj_diff_lon * corr)):
            corrected_lat[entry] = proj_lat
            corrected_lon[entry] = proj_lon
        elif (orig_diff_lat > proj_diff_lat * corr):
            corrected_lat[entry] = proj_lat
        elif (orig_diff_lon > proj_diff_lon * corr):
            corrected_lon[entry] = proj_lon

    plot = __plt_signal_scatter(setup.ax1, setup.lon_data, setup.lat_data, setup.signal_data, setup.cm)
    plot2 = __plt_signal_scatter(setup.ax1, corrected_lon, corrected_lat, setup.signal_data, setup.cm2)
    __plt_set_bbox(plt, setup.map_bbox)
    __plt_set_label()
    __plt_set_colorbar(setup, plot)

    plt.show()

def __plt_set_label(x_label="Longitude", x_rot=0, y_label="Latitude", y_rot=90, title="Signal Power vs Position"):
    plt.ylabel(y_label, rotation=y_rot)
    plt.xlabel(x_label, rotation=x_rot)
    plt.title(title)

def __plt_set_colorbar(setup, plot, label="Signal Power(dBm)"):
    ax = plt.axes()
    # Make sure to prevent lat/long from being displayed in scientific
    # notation
    ax.ticklabel_format(useOffset=False)
    cax = setup.fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cbar = plt.colorbar(plot, cax = cax)
    cbar.ax.set_ylabel(label, rotation=270, labelpad=10)

def __plt_set_bbox(plt, bbox):
    plt.xlim(bbox[0][0], bbox[0][1])
    plt.ylim(bbox[0][2], bbox[0][3])

def __plt_signal_scatter(ax, lon_data, lat_data, signal_data, cm):
    return ax.scatter(lon_data, lat_data, zorder=1, alpha=1.0, s=20, c=signal_data, cmap=cm)

def __plt_points_scatter(ax, lon_data, lat_data, col="blue"):
    return ax.scatter(lon_data, lat_data, zorder=1, alpha=1.0, s=20, color=col)

def __get_tower_positions(towerlist):
    tower_lat_data = np.array([])
    tower_lon_data = np.array([])
    for tower in towerlist:
        tower_lat_data = np.concatenate([tower_lat_data, [float(tower.lat)]])
        tower_lon_data = np.concatenate([tower_lon_data, [float(tower.lon)]])
    return tower_lat_data, tower_lon_data

def __convert_to_xy(lat, lon):
    x, y, zn, zl = utm.from_latlon(lat, lon)
    return x, y, zn, zl

def __convert_to_latlon(x, y, zn, zl):
    lat, lon = utm.to_latlon(x, y, zn, zl)
    return lat, lon

def __advance_coordinates(x, y, speed, direction):
    # north is 0, east is 90
    x_advance = speed * -1 * math.cos(direction + math.pi/2)
    y_advance = speed * math.sin(direction + math.pi/2)
    adj_x = x + x_advance
    adj_y = y + y_advance

    return adj_x, adj_y

def __project_next_position(lat, lon, speed, direction):
    x, y, zn, zl = __convert_to_xy(lat, lon)
    adj_x, adj_y = __advance_coordinates(x, y, speed, direction)
    lat_proj, lon_proj = __convert_to_latlon(adj_x, adj_y, zn, zl)
    return lat_proj, lon_proj

def __get_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6373.0
    coords_one = (lat1, lon1)
    coords_two = (lat2, lon2)

    return geopy.distance.distance(coords_one, coords_two).km

# Equation 12 in A Random Walk Model of Wave Propagation
def __rwm_fpd_recv_pwr(c_val, dist, dens, ab):
    # Equation 8 in A Random Walk Model of Wave Propagation
    arg = 1 - (1 - ab)**2
    g_r = (ab * dens * math.exp(-1 * (1 - arg * dens * dist)) + (1 - y) * dens * dist * sp.special.kv(0, math.sqrt(arg)) * dens * dist) / (2*math.pi*dist)
    output = (c_val / (dist**2)) * (dist**2) * g_r / (dens * ab)
    return output
