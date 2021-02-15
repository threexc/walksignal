#!/usr/bin/python3 
import csv
import sys
import numpy as np
import scipy.special as sp
import time
import utm
import math
import argparse
import requests
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
from geopy import distance
import walksignal.data as data
import walksignal.plottools as plottools
import walksignal.towers as towers
import walksignal.utils as utils

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class PlotData:
    def __init__(self, datafile, reference_file):
        self.dataset = data.DataSet(datafile)
        self.tower_list = towers.TowerList(self.dataset.data_matrix, reference_file)
        self.tower_lat_data = self.tower_list.lats
        self.tower_lon_data = self.tower_list.lons
        self.lat_data = self.dataset.lat
        self.lon_data = self.dataset.lon
        self.signal_data = self.dataset.signal_range
        self.rating = self.dataset.rating
        self.speed_values = self.dataset.speed_values
        self.direction = self.dataset.direction
        self.mcc = self.dataset.mcc
        self.mnc = self.dataset.mnc
        self.lac = self.dataset.lac
        self.cellid = self.dataset.cellid
        self.mcc_u = np.unique(self.mcc)
        self.mnc_u = np.unique(self.mnc)
        self.lac_u = np.unique(self.lac)
        self.cellid_u = np.unique(self.cellid)
        self.plot_map = None
        self.map_bbox = None
        self.get_map_and_bbox()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.set_image()
        self.cm = plt.cm.get_cmap('gist_heat')
        self.cm2 = plt.cm.get_cmap('gist_gray')
        self.avg_lat_diff = np.average(np.ediff1d(self.lat_data))
        self.avg_lon_diff = np.average(np.ediff1d(self.lon_data))
        self.distances = np.array([])
        self.plotrange = np.linspace(1, 500, 250)

    def get_map_and_bbox(self):
        self.plot_map = plt.imread(self.dataset.map_path)
        self.map_bbox = [entry for entry in utils.get_bbox(self.dataset.bbox_path)]

    def set_image(self):
        self.ax1.imshow(self.plot_map, zorder=0, extent = self.map_bbox[0], aspect="equal")

def plot_rating(datafile, reference_file):
    setup = PlotData(datafile, reference_file)

    signals = plt_signal_scatter(setup.ax1, setup.lon_data, setup.lat_data, setup.rating, setup.cm)
    tower_plot = plt_points_scatter(setup.ax1, setup.tower_lon_data, setup.tower_lat_data, "blue")
    plt_set_bbox(plt, setup.map_bbox)
    plt_set_label(title="Rating vs Position")
    plt_set_colorbar(setup, signals, "Rating (m)")
    
    plt.show()

def plot_data(x_axis, y_axis, annotation=None, x_label="X", y_label="Y", plot_title="X vs Y"):
    scatter = plt_points_scatter(x_axis, y_axis, c = annotation, s = 2)
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
    setup = PlotData(datafile, reference_file)
    corrected_lat = []
    corrected_lon = []

    for entry in range(len(setup.lat_data)):
        corrected_lat.append(setup.lat_data[entry])
        corrected_lon.append(setup.lon_data[entry])
    for entry in range(len(setup.lat_data) - 1):
        corr = 1.01
        proj_lat, proj_lon = utils.project_next_position(setup.lat_data[entry], setup.lon_data[entry], setup.speed_values[entry], setup.direction[entry])
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

    plot = plt_signal_scatter(setup.ax1, setup.lon_data, setup.lat_data, setup.signal_data, setup.cm)
    plot2 = plt_signal_scatter(setup.ax1, corrected_lon, corrected_lat, setup.signal_data, setup.cm2)
    plt_set_bbox(plt, setup.map_bbox)
    plt_set_label()
    plt_set_colorbar(setup, plot)

    plt.show()

def plot_gsp(datafile, reference_file):
    setup = PlotData(datafile, reference_file)

    signals = plt_signal_scatter(setup.ax1, setup.lon_data, setup.lat_data, setup.signal_data, setup.cm)
    tower_plot = plt_points_scatter(setup.ax1, setup.tower_lon_data, setup.tower_lat_data, "blue")
    plt_set_bbox(plt, setup.map_bbox)
    plt_set_label()
    plt_set_colorbar(setup, signals)

    plt.show()

def plot_towerdata(datafile, reference_file, mcc, mnc, lac, cellid):
    setup = PlotData(datafile, reference_file)
    plot_tower = None

    for tower in setup.tower_list.tower_list:
        if ((tower.mcc == mcc) and (tower.mnc == mnc) and (tower.lac == lac) and (tower.cellid == cellid)):
            plot_tower = tower

    if plot_tower is None:
        print("Tower not found based on inputs")
        sys.exit()

    points = plot_tower.data_points
    lon_series = np.array([point.lon for point in points], dtype=float)
    lat_series = np.array([point.lat for point in points], dtype=float)

    plot = plt_signal_scatter(setup.ax1, lon_series, lat_series, plot_tower.signal_power, setup.cm)
    plot2 = plt_points_scatter(setup.ax1, float(plot_tower.lon), float(plot_tower.lat))

    plt_set_bbox(plt, setup.map_bbox)
    plt_set_label()
    plt_set_colorbar(setup, plot)

    plt.show()

    plt.xlabel("Distances (m)")
    plt.ylabel("Power (dBm)")
    plt.grid()

    plt.suptitle("Power vs Distance")
    plt.plot(plot_tower.distances, plot_tower.signal_power, 'o', color='black')

    rwm_x = np.linspace(1, 350, 250) 

    plt_rwm_fpd2d(0.2, 0.5, rwm_x, color="blue")
    plt_rwm_fpd2d(0.5, 0.5, rwm_x, color="blue", marker="--")
    plt_rwm_fpd2d(0.5, 0.2, rwm_x, color="blue", marker="-.")
    plt_rwm_fpd2d(0.2, 0.2, rwm_x, color="blue", marker=":")

    plt_rwm_fpd3d(0.2, 0.5, rwm_x, color="red")
    plt_rwm_fpd3d(0.5, 0.5, rwm_x, color="red", marker="--")
    plt_rwm_fpd3d(0.5, 0.2, rwm_x, color="red", marker="-.")
    plt_rwm_fpd3d(0.2, 0.2, rwm_x, color="red", marker=":")

    plt.show()

def plt_set_label(x_label="Longitude", x_rot=0, y_label="Latitude", y_rot=90, title="Signal Power vs Position"):
    plt.ylabel(y_label, rotation=y_rot)
    plt.xlabel(x_label, rotation=x_rot)
    plt.title(title)

def plt_set_colorbar(setup, plot, label="Signal Power(dBm)"):
    ax = plt.axes()
    # Make sure to prevent lat/long from being displayed in scientific
    # notation
    fmtr = ticker.FormatStrFormatter('% 1.4f')
    cax = setup.fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cbar = plt.colorbar(plot, cax = cax)
    cbar.ax.set_ylabel(label, rotation=270, labelpad=10)
    ax.xaxis.set_major_formatter(fmtr)
    ax.yaxis.set_major_formatter(fmtr)

def plt_set_bbox(plt, bbox):
    plt.xlim(bbox[0][0], bbox[0][1])
    plt.ylim(bbox[0][2], bbox[0][3])

def plt_signal_scatter(ax, lon_data, lat_data, signal_data, cm):
    return ax.scatter(lon_data, lat_data, zorder=1, alpha=1.0, s=20, c=signal_data, cmap=cm)

def plt_points_scatter(ax, lon_data, lat_data, col="blue"):
    return ax.scatter(lon_data, lat_data, zorder=1, alpha=1.0, s=20, color=col)

# Equation 12 in A Random Walk Model of Wave Propagation
def plt_rwm_fpd2d(obs_dens, absorption, x_range, color="red", marker="-"):
    external_multiplier = obs_dens * absorption / (2 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    bessel = internal_multiplier * sp.kv(0, exp_mult_1 * x_range)
    first_component = internal_multiplier * np.multiply(x_range, bessel)
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    plt.plot(x_range, rwm_y, linestyle=marker, color=color)

# Equation 12 in A Random Walk Model of Wave Propagation
def plt_rwm_fpd3d(obs_dens, absorption, x_range, color="red", marker="-"):
    external_multiplier = obs_dens * absorption / (4 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    first_component = internal_multiplier * np.multiply(x_range, np.exp(-1 * exp_mult_1 * x_range))
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    plt.plot(x_range, rwm_y, linestyle=marker, color=color)

# Equation 12 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd2d(obs_dens, absorption, x_range):
    external_multiplier = obs_dens * absorption / (2 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    bessel = internal_multiplier * sp.kv(0, exp_mult_1 * x_range)
    first_component = internal_multiplier * np.multiply(x_range, bessel)
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y

# Equation 12 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd3d(obs_dens, absorption, x_range):
    external_multiplier = obs_dens * absorption / (4 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    first_component = internal_multiplier * np.multiply(x_range, np.exp(-1 * exp_mult_1 * x_range))
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y
