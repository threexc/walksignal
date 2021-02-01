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

    plot_two_ll(lat_data, lon_data, tower_lat_data, tower_lon_data, plot_map, map_bbox, signal_data)

def plot_rating(datafile, reference_file):
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
    np.set_printoptions(threshold=sys.maxsize)

    # Plot the data on the map
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.imshow(plot_map, zorder=0, extent = map_bbox, aspect = "equal")
    cm = plt.cm.get_cmap('gist_heat')
    plot = ax1.scatter(lon_data, lat_data, zorder=1, alpha=1.0, c=dataset.rating, cmap=cm, s=40)
    ax1.scatter(tower_lon_data, tower_lat_data, zorder=1, alpha=1.0, color="blue")
    plt.xlim(map_bbox[0], map_bbox[1])
    plt.ylim(map_bbox[2], map_bbox[3])
    plt.ylabel("Latitude", rotation=90)
    plt.xlabel("Longitude", rotation=0)
    plt.title("Rating vs Position")
    ax = plt.axes()

    # Make sure to prevent lat/long from being displayed in scientific
    # notation
    ax.ticklabel_format(useOffset=False)
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cbar = plt.colorbar(plot, cax = cax)
    cbar.ax.set_ylabel("GPS Rating (m)", rotation=270, labelpad=10)

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
    avg_lat_diff = np.average(np.ediff1d(lat_data))
    avg_lon_diff = np.average(np.ediff1d(lon_data))
    
    corrected_lat = np.array(dataset.data_matrix[1:,4], dtype=float)
    corrected_lon = np.array(dataset.data_matrix[1:,5], dtype=float)
    for entry in range(len(lat_data) - 1):
        corr = 1.2
        proj_lat, proj_lon = project_next_position(lat_data[entry], lon_data[entry], dataset.speed_values[entry], dataset.direction[entry])
        proj_diff_lat = np.absolute(lat_data[entry] - proj_lat)
        proj_diff_lon = np.absolute(lon_data[entry] - proj_lon)
        orig_diff_lat = np.absolute(lat_data[entry] - lat_data[entry+1])
        orig_diff_lon = np.absolute(lon_data[entry] - lon_data[entry+1])
        print(proj_diff_lat, orig_diff_lat, proj_diff_lon, orig_diff_lon)

        if ((orig_diff_lat > proj_diff_lat * corr) and (orig_diff_lon > proj_diff_lon * corr)):
            corrected_lat[entry] = proj_lat
            corrected_lon[entry] = proj_lon
        elif (orig_diff_lat > proj_diff_lat * corr):
            corrected_lat[entry] = proj_lat
        elif (orig_diff_lon > proj_diff_lon * corr):
            corrected_lon[entry] = proj_lon

        #if ((orig_diff_lat > avg_lat_diff * corr) and (orig_diff_lon > avg_lon_diff * corr)):
        #    corrected_lat[entry] = proj_lat
        #    corrected_lon[entry] = proj_lon
        #elif (orig_diff_lat > avg_lat_diff * corr):
        #    corrected_lat[entry] = proj_lat
        #elif (orig_diff_lon > avg_lon_diff * corr):
        #    corrected_lon[entry] = proj_lon

    # Plot the data on the map
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.imshow(plot_map, zorder=0, extent = map_bbox, aspect = "equal")
    cm = plt.cm.get_cmap('gist_heat')
    cm2 = plt.cm.get_cmap('gist_gray')
    plot = ax1.scatter(lon_data, lat_data, zorder=1, alpha=1.0, c=signal_data, cmap=cm, s=40)
    ax1.scatter(corrected_lon, corrected_lat, zorder=1, alpha=1.0, c=signal_data, cmap=cm2, s=40)
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

def plot_two_ll(lat_data_1, lon_data_1, lat_data_2, lon_data_2, plot_map, map_bbox, signal_data):
    # Plot the data on the map
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = setup_plot_image(ax1, plot_map, map_bbox)
    cm = plt.cm.get_cmap('gist_heat')
    signals = signal_scatter(ax1, lon_data_1, lat_data_1, signal_data, cm)
    towers = points_scatter(ax1, lon_data_2, lat_data_2)
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
    cbar = plt.colorbar(signals, cax = cax)
    cbar.ax.set_ylabel("Signal Power (dBm)", rotation=270, labelpad=10)

    plt.show()

def setup_plot_image(ax, plot_map, map_bbox):
    return ax.imshow(plot_map, zorder=0, extent = map_bbox, aspect="equal")

def signal_scatter(ax, lon_data, lat_data, signal_data, cm):
    return ax.scatter(lon_data, lat_data, zorder=1, c=signal_data, cmap=cm)

def points_scatter(ax, lon_data, lat_data, col="blue"):
    return ax.scatter(lon_data, lat_data, zorder=1, alpha=1.0, color=col)

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
    x, y, zn, zl = utm.from_latlon(lat, lon)
    return x, y, zn, zl

def convert_to_latlon(x, y, zn, zl):
    lat, lon = utm.to_latlon(x, y, zn, zl)
    return lat, lon

def advance_coordinates(x, y, speed, direction):
    # north is 0, east is 90
    x_advance = speed * 5 * -1 * math.cos(direction + math.pi/2)
    y_advance = speed * 5 * math.sin(direction + math.pi/2)
    adj_x = x + x_advance
    adj_y = y + y_advance

    return adj_x, adj_y

def project_next_position(lat, lon, speed, direction):
    x, y, zn, zl = convert_to_xy(lat, lon)
    adj_x, adj_y = advance_coordinates(x, y, speed, direction)
    lat_proj, lon_proj = convert_to_latlon(adj_x, adj_y, zn, zl)
    return lat_proj, lon_proj

def get_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6373.0
    coords_one = (lat1, lon1)
    coords_two = (lat2, lon2)

    return geopy.distance.distance(coords_one, coords_two).km

# Equation 12 in A Random Walk Model of Wave Propagation
def rwm_fpd_recv_pwr(c_val, dist, dens, ab):
    # Equation 8 in A Random Walk Model of Wave Propagation
    arg = 1 - (1 - ab)**2
    g_r = (ab * dens * math.exp(-1 * (1 - arg * dens * dist)) + (1 - y) * dens * dist * sp.special.kv(0, math.sqrt(arg)) * dens * dist) / (2*math.pi*dist)
    output = (c_val / (dist**2)) * (dist**2) * g_r / (dens * ab)
    return output
