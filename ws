#!/usr/bin/env python3
import argparse
import walksignal.plottools as pt

parser = argparse.ArgumentParser() 
group = parser.add_mutually_exclusive_group()
group.add_argument("--gsp", action="store_true")
group.add_argument("--pos", action="store_true")
group.add_argument("--rating", action="store_true")
group.add_argument("--tower", action="store_true")
parser.add_argument("--reference", required=True) 
parser.add_argument("--dataset", required=True) 
parser.add_argument("--cellid", required=False)
parser.add_argument("--lac", required=False)
parser.add_argument("--mnc", required=False)
parser.add_argument("--mcc", required=False)
results = parser.parse_args() 

if results.tower:
    if (not results.mcc) or (not results.mnc) or (not results.lac) or (not results.cellid):
        print("All four arguments --mcc, --mnc, --lac, and --cellid are required if using the --tower option")
    else:
        pt.plot_towerdata(results.dataset, results.reference, results.mcc, results.mnc, results.lac, results.cellid)
elif results.gsp:
    pt.plot_gsp(results.dataset, results.reference)
elif results.rating:
    pt.plot_rating(results.dataset, results.reference)
elif results.pos:
    pt.plot_positioning(results.dataset, results.reference)
else:
    pt.plot_gsp(results.dataset, results.reference)
