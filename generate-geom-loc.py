#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generates csv files of the form "passive-static_<subject_id>.csv"

usage:
    generateom-loc <subject_id> <run_id>

optional arguments:
  -h, --help              Show this help message and exit
"""

import csv
import os
import docopt
import random
import datetime
import numpy as np


def generate_csv(path):
    """Blabla This is useful"""
    writer = csv.writer(open(path, mode='w'), delimiter='\t',)
    offset = 0
    ref_list = ['face', 'text', 'tool', 'number', 'shapes', 'house', 'checker']
    dirs_list = ref_list.copy()
    random.shuffle(dirs_list)
    for _ in range(4):
        new_sample = random.sample(ref_list, 7)
        while new_sample[0] == dirs_list[6]:
            new_sample = random.sample(ref_list, 7)
        dirs_list += new_sample

    # Where will we put the star?
    positions = dict()
    for dirs in ref_list:
        reps = random.sample(range(0, 4), 3)
        positions[dirs] = [(reps[0], random.randint(6, 20)),
                           (reps[1], random.randint(6, 20)),
                           (reps[2], random.randint(6, 20))]
    count = {k: 0 for k in ref_list}
    inter_time = []
    while (len(inter_time) < len(dirs_list)):
        inter_time += [4000, 6000, 8000]
    random.shuffle(inter_time)
    for k, dirs in enumerate(dirs_list):
        bp = os.path.join("stim/STIM_DIR", dirs)
        if dirs == 'checker':
            files = np.tile(["checker01.png", "checker02.png"], 10)
        else:
            files = [os.path.join(dirs, f)
                     for f in os.listdir(bp)
                     if os.path.isfile(os.path.join(bp, f))]
            random.shuffle(files)
        for i, f in enumerate(files):
            writer.writerow([offset, "picture", f])
            offset += 100
            writer.writerow([offset, "picture", "stimblank.png"])
            offset += 200
            if (count[dirs], i) in positions[dirs]:
                writer.writerow([offset, "picture", "Star.png"])
                offset += 100
                writer.writerow([offset, "picture", "stimblank.png"])
                offset += 200
        offset += inter_time[k]
        count[dirs] += 1
    print(f"Total duration is {str(datetime.timedelta(milliseconds=offset))}")


if __name__ == "__main__":
    args = docopt.docopt(__doc__, version='0.0.1')
    s_id = args["<subject_id>"]
    r_id = args["<run_id>"]
    generate_csv(f"stim/geom-loc_{s_id}_{r_id}.csv")
