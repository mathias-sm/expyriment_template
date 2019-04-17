#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Breaks csv file's rsvp and pictseq into explicit csvs with text/picture

This script takes an input csv file and, for each line of stype rsvp (resp.
pictseq) it splits them into several lines, it outputs several alternating
lines of stype text (resp. picture) and blank according to the optional
arguments of duration and ISI.

NOTE : it assumes that you know what you're doing to some extent. Indeed if you
have rsvps/pictseq that contain only one element, it will not *just* replace
them with an associated text/picture line, but will still insert a blank
afterward. If this is not what you need either modify this script to specify
what you want — unless `sed -i 's/rsvp/text/'` is enough for your case?

Usage:
    seq_breaker.py toto [(--neg R G B)]
    seq_breaker.py [options] <in_file> [<out_file>]

Options:
    -h --help             Show this screen.
"""

# Documentation
from docopt import docopt

# Other
import tqdm
import csv
import sys

if __name__ == "__main__":

    args = docopt(__doc__, version='0.0.1')
    print(args)

    # Shorthands for latter computations
    td = int(args["--text-duration"])
    ti = int(args["--text-isi"])
    pd = int(args["--pict-duration"])
    pi = int(args["--pict-isi"])

    csvFile = open(args["<in_file>"], 'r')
    lines = [line for line in csvFile]

    out = args["<out_file>"]
    o = open(out, 'w') if out is not None else sys.stdout

    output = csv.writer(o, delimiter='\t')

    for row in tqdm.tqdm(csv.reader(lines, delimiter='\t'), total=len(lines)):
        cond, onset, stype, f = row
        if stype == "rsvp":
            for i, e in enumerate(f.split(",")):
                computed_onset = int(onset) + (i * (td + ti))
                output.writerow([cond, computed_onset, "text", e])
                output.writerow([cond, computed_onset + ti, "blank", "blank"])
        elif stype == "pictseq":
            for i, e in enumerate(f.split(",")):
                computed_onset = int(onset) + (i * (pd + pi))
                output.writerow([cond, computed_onset, "picture", e])
                output.writerow([cond, computed_onset + pi, "blank", "blank"])
        else:
            output.writerow(row)
