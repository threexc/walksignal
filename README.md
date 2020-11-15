# ociplot
Plot OpenCellID data on street maps and other images

Example:

![Downtown Ottawa](example.png?raw=true)


## Usage

To display one or more data sets as separate charts:
`python3 ociplot.py --compare --list [file1] [file2] ... [fileN]`

To combine all data into a single plot:
`python3 ociplot.py --combine --list [file1] [file2] ... [fileN]`

For example,
`python3 ociplot.py --compare --list /data/laycolyoc/Open*`

In both cases, one of either --compare or --combine is required, as is
--list.


## TODO

- Clean up plotting code
- Add more command-line options
- Start work on a GUI with more display features
