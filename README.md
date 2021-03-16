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

GUI:

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
   same path as the map file and the data as "bbox.txt". This can be
   obtained on the same page as the export of the map image

### Pruning Data Sets

prune_data should first be used on any data files to create versions of them
that don't include any empty cells for the various columns. These modified
files are created in the same folder with the .pruned extension.

Example:

`./prune_data data/lacolyoc/OpenCellID_2020*`

### Using gws

Run the following to start the GUI:
`./gws`

A reference file and a datafile must both be selected. Selecting a
datafile with the load button automatically loads the dataset for use. 

The plot tab and map tab are both updated when selecting the "Load Tower
Data" button.

### Using ws

The `ws` tool can be used to plot the following types of plots:

For the entire data set:
- Geospatial power measurements ("--gsp")
- GPS rating ("--rating")
- GPS positioning correction ("--pos")

For a specific tower (also requires "--mcc", "--mnc", "--lac", and "--cellid" with numeric values):
- Geospatial power measurements and power vs range plots ("--tower")

In both cases, the reference file ("--reference") and dataset ("--dataset")
are required.

Examples:

`./ws --tower --reference data/oci_ref/302.csv --dataset data/uottawa/combined_data.csv.pruned --cellid 9552457 --lac 29100 --mnc 720 --mcc 302`

`./ws --pos --reference data/oci_ref/302.csv --dataset data/uottawa/combined_data.csv.pruned`

`./ws --gsp --reference data/oci_ref/302.csv --dataset data/uottawa/combined_data.csv.pruned`

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
- Add option to identify tower associated with a given data point,
  including range
- Optimize for faster parsing and plotting, including possibly by adding
  script to concatenate all data before reading
- Start work on a GUI with more display features
- Identify other insightful ways to display data
