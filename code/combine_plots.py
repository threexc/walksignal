#!/usr/bin/python3 
import csv
import sys
import numpy as np
import time
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from ocireader import *

def compare_plots(argv):
    # Get the list of arguments after the filename
    files = argv[1:]
    figs = {}
    axs = {}
    lon_data = np.array([])
    lat_data = np.array([])
    signal_data = np.array([])

    for i, plot in enumerate(files):
        dataset = DataSet(files[i])
        dataset.read_data()
        plotter = SignalPlotter(dataset)
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
    ax = plt.axes()
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    plt.colorbar(plot, cax = cax)

    plt.show()


if __name__ == "__main__":
    compare_plots(sys.argv)
