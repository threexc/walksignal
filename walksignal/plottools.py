#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import utm
import math
import argparse
import requests
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.data as data
import walksignal.plottools as plottools
import walksignal.towers as towers
import walksignal.utils as utils


def plot_gsp(datafile, reference_file):
    figs = {}
    axs = {}
    signal_data = np.array([])
    tower_list = []
    tower_lat_data = np.array([])
    tower_lon_data = np.array([])
    dataset = None
    plottools = None
    map_bbox = None
    towerset = None

    dataset = data.DataSet(datafile)
    towerlist = towers.TowerList(datafile, reference_file)
    

    tower_lat_data, tower_lon_data = get_tower_positions(towerlist.tower_list)
    plot_map, map_bbox = get_map_and_bbox(dataset.map_path, utils.get_bbox(dataset.bbox_path)[0])
    
    lat_data = np.array(dataset.data_matrix[1:,4], dtype=float)
    lon_data = np.array(dataset.data_matrix[1:,5], dtype=float)
    signal_data = np.array(dataset.data_matrix[1:,6], dtype=float)

    # Plot the data on the map
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

def plot_positioning(datafile, reference_file):
    figs = {}
    axs = {}
    signal_data = np.array([])
    tower_list = []
    tower_lat_data = np.array([])
    tower_lon_data = np.array([])
    dataset = None
    plottools = None
    map_bbox = None
    towerset = None

    dataset = data.DataSet(datafile)
    plot_map, map_bbox = get_map_and_bbox(dataset.map_path, utils.get_bbox(dataset.bbox_path)[0])
    
    lat_data = np.array(dataset.data_matrix[1:,4], dtype=float)
    lon_data = np.array(dataset.data_matrix[1:,5], dtype=float)
    signal_data = np.array(dataset.data_matrix[1:,6], dtype=float)
    
    lat_list = []
    lon_list = []
    for entry in range(len(lat_data)):
        proj_lat, proj_lon = project_next_position(lat_data[entry], lon_data[entry], dataset.speed_values[entry], dataset.direction[entry])
        lat_list.append(proj_lat)
        lon_list.append(proj_lon)

    proj_lats = np.array(lat_list, dtype=float)
    proj_lons = np.array(lon_list, dtype=float)

    # Plot the data on the map
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.imshow(plot_map, zorder=0, extent = map_bbox, aspect = "equal")
    cm = plt.cm.get_cmap('gist_heat')
    cm2 = plt.cm.get_cmap('gist_gray')
    plot = ax1.scatter(lon_data, lat_data, zorder=1, alpha=1.0, c=signal_data, cmap=cm, s=40)
    ax1.scatter(proj_lons, proj_lats, zorder=1, alpha=1.0, c=signal_data, cmap=cm2, s=40)
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


def get_tower_positions(towerlist):
    tower_lat_data = np.array([])
    tower_lon_data = np.array([])
    for tower in towerlist:
        tower_lat_data = np.concatenate([tower_lat_data, [float(tower.lat)]])
        tower_lon_data = np.concatenate([tower_lon_data, [float(tower.lon)]])
    return tower_lat_data, tower_lon_data

def get_map_and_bbox(plot_map, map_bbox):
    plt_map = plt.imread(plot_map)
    plt_bbox = [entry for entry in map_bbox]
    return plt_map, plt_bbox

def convert_to_xy(lat, lon):
    print(lat)
    print(type(lat))
    x, y, zn, zl = utm.from_latlon(lat, lon)
    return x, y, zn, zl

def convert_to_latlon(x, y, zn, zl):
    lat, lon = utm.to_latlon(x, y, zn, zl)
    return lat, lon

def advance_coordinates(x, y, speed, direction):
    # north is 0, east is 90
    x_advance = speed * -1 * math.cos(direction + math.pi/2)
    y_advance = speed * math.sin(direction + math.pi/2)
    adj_x = x + x_advance
    adj_y = y + y_advance

    return adj_x, adj_y

def project_next_position(lat, lon, speed, direction):
    x, y, zn, zl = convert_to_xy(lat, lon)
    adj_x, adj_y = advance_coordinates(x, y, speed, direction)
    lat_proj, lon_proj = convert_to_latlon(adj_x, adj_y, zn, zl)
    return lat_proj, lon_proj
