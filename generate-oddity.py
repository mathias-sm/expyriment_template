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
import os
import numpy as np

from math import cos, sin, pi, acos


def min_dist(l):
    local_min = 999
    for i in range(len(l)):
        for j in range(len(l) - i - 1):
            local_min = min(local_min, abs(l[i] - l[i+j+1]))
    return local_min


def rot_m(a):
    a = (a/360)*(2*pi)
    return np.array(((cos(a), -sin(a)),
                     (sin(a), cos(a))))


def rotate(v, theta):
    return theta.dot(v)


def dilate(v, dil):
    return [x*dil for x in v]


def vadd(v1,v2):
    return [a+b for a,b in zip(v1,v2)]


def outlierize(shape):

  # Issue : y axis is all wrong... Here be changes.
  shape = [np.array((x, -y)) for x, y in shape]

  v1 = shape[0]
  v2 = shape[1]
  v3 = shape[2]
  b = v3 - v2
  c = v3 - v1
  d = v1 - v2

  mean = sum([np.linalg.norm(x) for x in [v1,v2,v3,b,c,d]]) / 6

  d1 = 0.3 * mean
  d2 = np.linalg.norm(b)

  norb = (d1/d2)*b
  alpha = rot_m((acos(((d1*d1)-(2*d2*d2))/(2*d2*d2))/2)*(360/(2*pi)))

  o1 = v3 - norb
  o2 = v3 + norb
  o3 = v3 + rotate(norb, alpha)
  o4 = v3 + rotate(norb, -alpha)

  o1, o2, o3, o4 = [[shape[0], shape[1], x] for x in [o1,o2,o3,o4]]

  return [shape, o1, o2, o3, o4]


def generate_csv(s_id, r_id):

    refDilations = [0.875, 0.925, 0.975, 1.025, 1.075, 1.125]
    refAngles = [rot_m(a) for a in [-25, -15, -5, 5, 15, 25]]

    fix_param = "20;2;0;127;0"

    writer = csv.writer(open(f"stim/oddity_{s_id}_{r_id}.csv", mode='w'), delimiter='\t',)
    offset = 0
    shapes = json.load(open("shapes.json", mode="r"))
    shapes = {shape: outlierize(shapes[shape]) for shape in shapes.keys()}
    names = list(shapes.keys())
    # names += ["color_1", "color2"]
    randomized_pos = {k: [] for k in names}
    randomized_type = {k: [] for k in names}
    random.shuffle(names)
    for i, shape in enumerate(names):
        randomized_pos[shape] = list(range(6))
        random.shuffle(randomized_pos[shape])
        l2 = list(range(6))
        random.shuffle(l2)
        while randomized_pos[shape][5] == l2[0]:
            random.shuffle(l2)
        l2 = l2[0:4]
        randomized_pos[shape] += l2

        randomized_type[shape] = list(range(4))
        random.shuffle(randomized_type[shape])
        l2 = list(range(4))
        random.shuffle(l2)
        while randomized_type[shape][3] == l2[0]:
            random.shuffle(l2)
        randomized_type[shape] += l2
        random.shuffle(l2)
        while randomized_type[shape][7] == l2[0]:
            random.shuffle(l2)
        l2 = l2[0:2]
        randomized_type[shape] += l2
        randomized_type[shape] = [x + 1 for x in randomized_type[shape]]

    if not os.path.exists(f"stim/oddity_{s_id}_{r_id}/"):
        os.makedirs(f"stim/oddity_{s_id}_{r_id}/")

    for i, shape_name in enumerate(names):
        for j in range(10):
            dils = list(np.random.permutation(range(6)))
            rots = list(np.random.permutation(range(6)))
            out_pos = randomized_pos[shape_name][j]
            out_type = randomized_type[shape_name][j]
            stim_fname = f"stim/oddity_{s_id}_{r_id}/{shape_name}_{j}.csv"
            writer_stim = csv.writer(open(stim_fname, mode='w'), delimiter=';')

            metadata = [shape_name, dils, rots, out_pos, out_type]
            
            for k in range(6):
                # Here we should take care of the various outliers
                shape = []
                if k == out_pos:
                    shape = shapes[shape_name][out_type]
                else:
                    shape = shapes[shape_name][0]
                v1 = shape[0]
                v2 = shape[2] - shape[0]
                v3 = shape[1] - shape[2]
                v4 = -shape[1]
                vs = [v1, v2, v3, v4]
                # Now apply the transformation : rotation, dilation, and y
                # direction correction
                vs = [rotate(v, refAngles[rots[k]]) for v in vs]
                vs = [dilate(v, refDilations[dils[k]]) for v in vs]
                vs = [dilate(v, 75) for v in vs]
                writer_stim.writerow(vs)

            writer.writerow(["test", offset, "oddity", stim_fname] + metadata)
            offset += 200
            writer.writerow(["test", offset, "fix", fix_param] + ["","","","",""])
            offset += 4000

        writer.writerow(["test", offset, "fix", fix_param] + ["","","","",""])
        offset += ((np.random.choice([6, 8, 10], 1)[0]) * 1000) - 600
        writer.writerow(["test", offset, "fix", "10;2;0;127;0"] + ["","","","",""])
        offset += 600

    print(f"Total duration is {offset/1000/60}min")


if __name__ == "__main__":
    args = docopt.docopt(__doc__, version='0.0.1')
    s_id = args["<subject_id>"]
    r_id = args["<run_id>"]
    generate_csv(s_id, r_id)
