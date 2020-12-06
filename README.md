# walksignal
Plot OpenCellID data on street maps and other images

Example:

![Downtown Ottawa](example.png?raw=true)


## Usage

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
