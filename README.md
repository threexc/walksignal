# walksignal
walksignal is a set of tools to plot OpenCellID data on street maps and other
images. The project was originally motivated by interest in comparing
real-world data to random walk models in the context of signal reception and
quality. It relies heavily on the use of freely-available mobile apps and
online services:

1. [Network Cell Info Lite](https://play.google.com/store/apps/details?id=com.wilysis.cellinfolite&hl=en_CA&gl=US)
2. [OpenStreetMap](https://www.openstreetmap.org)
3. [OpenCellID](https://www.opencellid.org)

All due credit is given to the maintainers and communities around these tools
and services.

Example:

![Downtown Ottawa](example.png?raw=true)

## Usage

### Python Modules

walksignal uses the following Python modules:

- numpy
- matplotlib
- argparse
- csv

### Basic Data Requirements

Although example data can be found in the data/ subfolder, the tools here are
designed to work with other datasets. In order to compile a dataset for use,
the following things are required:

1. At least one set of OpenCellID data, such as that exported by the Network
   Cell Info Lite app
2. A map image exported from the OpenStreetMap site, which contains the area of
   interest (if plotting spatial data such as in the example)
3. A map boundary box, defined as min/max lat/long readings, defined in the
   same path as the map file and the data as "bbox.txt"

### Pruning Data Sets

prune_data should first be used on any data files to create versions of them
that don't include any empty cells for the various columns. These modified
files are created in the same folder with the .pruned extension.

Example:

`./prune_data data/lacolyoc/OpenCellID_2020*`

### Using com_plot

com_plot allows visualizing the signal strength as a heatmap on a map generated
with OpenStreetMap. Currently this only supports the map for the example data.

To display one or more data sets as separate charts:
`./com_plot --compare --list [file1] [file2] ... [fileN]`

To combine all data into a single plot:
`./com_plot --combine --list [file1] [file2] ... [fileN]`

In both cases, one of either --compare or --combine is required, as is
--list.

### Using plot_pair

To plot a scatter of two input parameters:
`./plot_pair -x [parameter1] -y [parameter2] --list data/lacolyoc/OpenCellID_2020\*.pruned`

Possible parameters are:

1. time
2. signal_strength
3. pcis
4. mcc
5. mnc
6. cellid
7. rating
8. direction
9. advanced

For example,

`./plot_pair -x time -y signal_strength --list data/lacolyoc/OpenCellID_2020\*.pruned`

or

`./plot_pair -x cellid -y advance --list data/lacolyoc/OpenCellID_2020\*.pruned`

## TODO

- Clean up plotting code
- Add more command-line options
- Start work on a GUI with more display features
