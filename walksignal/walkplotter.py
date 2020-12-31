#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import argparse
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import walksignal.walkreader as walkreader

def compare_plots(files):
    figs={}
    axs={}
    for i, datafile in enumerate(files):
        dataset = walkreader.DataSet(datafile)
        plotter = walkreader.SignalPlotter(dataset)
        map_file = plt.imread(plotter.map_file)
        map_bbox = (-75.70629, -75.69213, 45.41321, 45.41976)
        ax = plt.subplot(len(files), 1, i+1)

        pcm = ax.scatter(plotter.spatial_lon,
                plotter.spatial_lat, zorder=1, alpha=1.0,
                c=plotter.signal_range, cmap='gist_heat', s=40)
        ax.set_xlim(map_bbox[0], map_bbox[1])
        ax.set_ylim(map_bbox[2], map_bbox[3])
        plt.colorbar(pcm, ax=ax)
        im = ax.imshow(map_file, zorder=0, extent = map_bbox, aspect = "equal")

    plt.show()


def combine_plots(files):
    figs = {}
    axs = {}
    lon_data = np.array([])
    lat_data = np.array([])
    signal_data = np.array([])

    for datafile in files:
        dataset = walkreader.DataSet(datafile)
        plotter = walkreader.SignalPlotter(dataset)
        lon_data = np.concatenate([lon_data, plotter.spatial_lon])
        lat_data = np.concatenate([lat_data, plotter.spatial_lat])
        signal_data = np.concatenate([signal_data, plotter.signal_range])
    
    map_file = plt.imread(plotter.map_file)
    map_bbox = (-75.70629, -75.69213, 45.41321, 45.41976)
    fig = plt.figure()
    im = plt.imshow(map_file, zorder=0, extent = map_bbox, aspect = "equal")
    cm = plt.cm.get_cmap('gist_heat')

    plot = plt.scatter(lon_data,
            lat_data, zorder=1, alpha=1.0,
            c=signal_data, cmap=cm, s=40)
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

