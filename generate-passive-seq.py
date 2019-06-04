#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generates csv files of the form "passive-seq_<subject_id>.csv"

usage:
    generate-passive-seq <subject_id> <run_id>

optional arguments:
  -h, --help              Show this help message and exit
"""

import csv
import random
import json
import datetime
import docopt
import numpy as np

from math import cos, sin, pi, acos


def min_dist(l):
    local_min = 999
    for i in range(len(l)):
        for j in range(len(l) - i - 1):
            local_min = min(local_min, abs(l[i] - l[i+j+1]))
    return local_min


def max_x(vs): return max([a for a, b in vs])
def max_y(vs): return max([b for a, b in vs])
def min_x(vs): return min([a for a, b in vs])
def min_y(vs): return min([b for a, b in vs])


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


def generate_csv(path):

    refDilations = [0.875, 0.925, 0.975, 1.025, 1.075, 1.125]
    refAngles = [rot_m(a) for a in [-25, -15, -5, 5, 15, 25]]
    pt_on = 200
    pt_off = 50
    osa = 550

    fix_param = "20;4;0;127;0"
    fix_param_off = "15;2;0;127;0"

    writer = csv.writer(open(path, mode='w'), delimiter='\t',)
    offset = 0
    shapes = json.load(open("shapes.json", mode="r"))
    shapes = {shape: outlierize(shapes[shape]) for shape in shapes.keys()}
    names = list(shapes.keys())
    super_outlier_bloc_pos = ([1, 0] * len(names))
    random.shuffle(super_outlier_bloc_pos)
    mruns = [(([0]*20), ([0]*20), ([0]*20)) for _ in range(len(names)*2)]
    mrun_shapes = names*2
    random.shuffle(mrun_shapes)
    used = {k: list(np.random.permutation([1, 2, 3, 4])) for k in names}
    for i, mrun in enumerate(mruns):
        pos = []
        outlier, rot, dil = mrun
        if super_outlier_bloc_pos[i] == 1:
            pos = np.random.choice(range(12), 3)
            while min_dist(pos) < 3:
                pos = np.random.choice(range(12), 3)
        else:
            pos = np.random.choice(range(12), 2)
            while min_dist(pos) < 3:
                pos = np.random.choice(range(12), 2)
        outlier[7+pos[0]] = used[mrun_shapes[i]].pop()
        outlier[7+pos[1]] = used[mrun_shapes[i]].pop()
        if super_outlier_bloc_pos[i] == 1:
            outlier[7+pos[2]] = 5
        rot[0] = random.randint(0, 5)
        dil[0] = random.randint(0, 5)
        for i in range(len(rot) - 1):
            rot[i+1] = random.randint(0, 5)
            dil[i+1] = random.randint(0, 5)
            while rot[i] == rot[i+1]:
                rot[i+1] = random.randint(0, 5)
            while dil[i] == dil[i+1]:
                dil[i+1] = random.randint(0, 5)
        mrun = outlier, rot, dil
    inter_time = []
    while (len(inter_time) < len(mruns)):
        inter_time += [4000, 6000, 8000]
    random.shuffle(inter_time)
    writer.writerow([offset, "fix", fix_param_off] + ["","","","",""])
    offset += 2000 - 600
    writer.writerow([offset, "fix", fix_param] + ["","","","",""])
    offset += 600
    for i, (outliers, rots, dils) in enumerate(mruns):
        for out, rot, dil in zip(outliers, rots, dils):
            shape = shapes[mrun_shapes[i]][out % 5] # maps 5 = star -> rule
            v1 = shape[0]
            v2 = shape[2] - shape[0]
            v3 = shape[1] - shape[2]
            v4 = -shape[1]
            vs = [v1, v2, v3, v4]

            # Now apply the transformation : rotation, dilation, and y
            # direction correction
            vs = [rotate(v, refAngles[rot]) for v in vs]
            vs = [dilate(v, refDilations[dil]) for v in vs]
            vs = [dilate(v, 100) for v in vs]

            # Turn vectors into points and check for correctness
            p1 = np.array([0,0])
            p2 = p1 + vs[0]
            p3 = p2 + vs[1]
            p4 = p3 + vs[2]
            ps = [p1,p2,p3,p4]
            j_size = 25
            j_x = np.random.randint(2 * j_size + 1) - j_size
            j_y = np.random.randint(2 * j_size + 1) - j_size
            ps = [x + [j_x , j_y] for x in ps]
            assert((abs(p1 - (p4 + vs[3])) < 0.0000001).all())

            metadata = [mrun_shapes[i], out, rot, dil, j_x, j_y]

            # Saddly, Expyriment uses the center of the bounding box, not
            # this one: barycenter = (p1 + p2 + p3 + p4) / 4     ;(
            center = [(max_x(ps) + min_x(ps))/2, (max_y(ps) + min_y(ps))/2]

            v_from_b = [v - center for v in [p1,p2,p3,p4]]
            stringified = [f"5;0;{x[0]};{x[1]}" for x in v_from_b]

            writer.writerow([offset, "dot", stringified[1]] + metadata)
            offset += pt_on
            writer.writerow([offset, "fix", fix_param] + metadata)
            offset += pt_off
            writer.writerow([offset, "dot", stringified[0]] + metadata)
            offset += pt_on
            writer.writerow([offset, "fix", fix_param] + metadata)
            offset += pt_off
            writer.writerow([offset, "dot", stringified[3]] + metadata)
            offset += pt_on
            writer.writerow([offset, "fix", fix_param] + metadata)
            offset += pt_off
            if out == 5:
                star_string = f"{v_from_b[2][0]};{v_from_b[2][1]};small_star.png"
                writer.writerow([offset, "small_star", star_string] \
                                + metadata)
            else:
                writer.writerow([offset, "dot", stringified[2]] \
                                + metadata)
            offset += pt_on
            writer.writerow([offset, "fix", fix_param] + metadata)
            offset += osa

        writer.writerow([offset, "fix", fix_param_off] + ["","","","",""])
        offset += (inter_time[i]) - 600
        writer.writerow([offset, "fix", fix_param])
        offset += 600

    print(f"Total duration is {str(datetime.timedelta(milliseconds=offset))}")


if __name__ == "__main__":
    args = docopt.docopt(__doc__, version='0.0.1')
    s_id = args["<subject_id>"]
    r_id = args["<run_id>"]
    generate_csv(f"stim/passive-seq_{s_id}_{r_id}.csv")
