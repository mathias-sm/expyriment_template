#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generates csv files of the form "passive-static_<subject_id>.csv"

usage:
    generate-oddity <subject_id> <run_id>

optional arguments:
  -h, --help              Show this help message and exit
"""

import csv
import random
import json
import docopt
import datetime
import os
import numpy as np

from math import cos, sin, pi, acos

def generate_csv(s_id, r_id):

    refDilations = [0.875, 0.925, 0.975, 1.025, 1.075, 1.125]
    refAngles = [-25, -15, -5, 5, 15, 25]  # May need deg2rad

    fix_param = "20;4;0;127;0"
    fix_param_off = "15;2;0;127;0"

    writer = csv.writer(open(f"generated/oddity-faces_{s_id}_{r_id}.csv", mode='w'), delimiter='\t',lineterminator='\n')
    offset = 0
    diff_levels = [3, 5, 7]  # Interpol distance between ref and out
    randomized_pos = {k: [] for k in diff_levels}
    random.shuffle(diff_levels)
    for i, diff in enumerate(diff_levels):
        randomized_pos[diff] = list(range(6))
        random.shuffle(randomized_pos[diff])
        l2 = list(range(6))
        random.shuffle(l2)
        while randomized_pos[diff][5] == l2[0]:
            random.shuffle(l2)
        l2 = l2[0:4]
        randomized_pos[diff] += l2

    inter_time = []
    while (len(inter_time) + 3 <= len(diff_levels)):
        inter_time += [4000, 6000, 8000]
    if (len(inter_time) + 2 == len(diff_levels)):
        inter_time += [4000, 8000]
    elif (len(inter_time) + 1 == len(diff_levels)):
        inter_time += [6000]
    random.shuffle(inter_time)

    if not os.path.exists(f"STIM_DIR/oddity-faces_{s_id}_{r_id}/"):
        os.makedirs(f"STIM_DIR/oddity-faces_{s_id}_{r_id}/")

    writer.writerow([offset, "fix", fix_param_off] + ["","","","",""])
    offset += 2000 - 600
    writer.writerow([offset, "fix", fix_param] + ["","","","",""])
    offset += 600
    for i, diff_level in enumerate(diff_levels):
        for j in range(10):
            dils = list(np.random.permutation(range(6)))
            rots = list(np.random.permutation(range(6)))
            out_pos = randomized_pos[diff_level][j]
            stim_fname = f"STIM_DIR/oddity-faces_{s_id}_{r_id}/{diff_level}_{j}.csv"
            writer_stim = csv.writer(open(stim_fname, mode='w'), delimiter=';', lineterminator='\n')

            face_rule_i = random.randint(0, 20 - diff_level)
            face_outlier_i = face_rule_i + diff_level
            face_rule = "C" + str(face_rule_i).rjust(2, '0') + ".png"
            face_outlier = "C" + str(face_outlier_i).rjust(2, '0') + ".png"

            for k in range(6):
                which_face = face_rule if k != out_pos else face_outlier
                writer_stim.writerow([which_face, refDilations[dils[k]], refAngles[rots[k]]])

            metadata = [diff_level, face_rule, face_outlier, dils, rots, out_pos]

            writer.writerow([offset, "oddity-faces", stim_fname] + metadata)
            offset += 2000
            writer.writerow([offset, "fix", fix_param] + ["","","","",""])
            offset += 4000
            if j == 4:
                writer.writerow([offset, "fix", fix_param] + ["","","","",""])
                offset += 4000

        writer.writerow([offset, "fix", fix_param_off] + ["","","","",""])
        offset += (inter_time[i]) - 600
        writer.writerow([offset, "fix", fix_param] + ["","","","",""])
        offset += 600

    print(f"Total duration is {str(datetime.timedelta(milliseconds=offset))}")
    print(f"Assume {2+int(offset/1000/1.81)}TRs")
    writer.writerow([offset, "fix", fix_param] + ["","","","",""])
    offset += 6000


if __name__ == "__main__":
    args = docopt.docopt(__doc__, version='0.0.1')
    s_id = args["<subject_id>"]
    r_id = args["<run_id>"]
    generate_csv(s_id, r_id)
