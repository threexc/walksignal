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
    figs={}
    axs={}
    for i, plot in enumerate(files):
        dataset = DataSet(files[i])
        dataset.read_data()
        plotter = SignalPlotter(dataset)
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


if __name__ == "__main__":
    compare_plots(sys.argv)
