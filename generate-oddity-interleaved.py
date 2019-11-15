#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generates csv files of the form "passive-static_<subject_id>.csv"

usage:
    generate-oddity <subject_id> <run_id> <shape_file> <mini_bloc_size> <mini_bloc_repeat> (face|noface)

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


def generate_csv(s_id, r_id, shape_file, face, mini_bloc_size, mini_bloc_repeat):

    refDilations = [0.875, 0.925, 0.975, 1.025, 1.075, 1.125]
    refAngles_base = [-25, -15, -5, 5, 15, 25]
    refAngles = [rot_m(a) for a in [-25, -15, -5, 5, 15, 25]]

    fix_param = "20;4;0;127;0"
    fix_param_off = "15;2;0;127;0"

    writer = csv.writer(open(f"generated/oddity-interleaved_{s_id}_{r_id}.csv", mode='w'), delimiter='\t',lineterminator='\n')
    offset = 0
    shapes = json.load(open(shape_file, mode="r"))
    shapes = {shape: outlierize(shapes[shape]) for shape in shapes.keys()}
    names = list(shapes.keys())
    if face:
        names += ["face_diff_1", "face_diff_2"]

    def generate_one(names):
        local_names = names.copy()
        random.shuffle(local_names)
        randomized_pos = [None] * len(names)
        randomized_type = [None] * len(names)
        for i, shape in enumerate(local_names):
            randomized_pos[i] = list(range(6))
            random.shuffle(randomized_pos[i])
            while (len(randomized_pos[i]) < mini_bloc_size):
                tmp = list(range(6))
                random.shuffle(tmp)
                while (randomized_pos[i][len(randomized_pos[i]) - 1] == tmp[0]):
                    random.shuffle(tmp)
                randomized_pos[i] += tmp

            randomized_type[i] = list(range(4))
            random.shuffle(randomized_type[i])
            while (len(randomized_type[i]) < mini_bloc_size):
                tmp = list(range(4))
                random.shuffle(tmp)
                while (randomized_type[i][len(randomized_type[i]) - 1] == tmp[0]):
                    random.shuffle(tmp)
                randomized_type[i] += tmp
            randomized_type[i] = [x + 1 for x in randomized_type[i]]

        return [local_names, randomized_pos, randomized_type]

    names_copy = names.copy()
    names, randomized_pos, randomized_type = generate_one(names_copy)
    for i in range(mini_bloc_repeat - 1):
        new_names, new_randomized_pos, new_randomized_type = generate_one(names_copy)
        while (names[len(names) - 1] == new_names[0]):
            new_names, new_randomized_pos, new_randomized_type = generate_one(names_copy)
        names = names + new_names
        randomized_pos = randomized_pos + new_randomized_pos
        randomized_type = randomized_type + new_randomized_type

    inter_time = []
    while (len(inter_time) + 3 <= len(names)):
        inter_time += [4000, 6000, 8000]
    if (len(inter_time) + 2 == len(names)):
        inter_time += [4000, 8000]
    elif (len(inter_time) + 1 == len(names)):
        inter_time += [6000]
    random.shuffle(inter_time)


    if not os.path.exists(f"STIM_DIR/oddity-interleaved_{s_id}_{r_id}/"):
        os.makedirs(f"STIM_DIR/oddity-interleaved_{s_id}_{r_id}/")

    writer.writerow([offset, "fix", fix_param_off] + ["","","","",""])
    offset += 2000 - 600
    writer.writerow([offset, "fix", fix_param] + ["","","","",""])
    offset += 600
    for i, shape_name in enumerate(names):
        for j in range(mini_bloc_size):
            dils = list(np.random.permutation(range(6)))
            rots = list(np.random.permutation(range(6)))
            out_pos = randomized_pos[i][j]
            stim_fname = f"STIM_DIR/oddity-interleaved_{s_id}_{r_id}/{shape_name}_{j}.csv"
            writer_stim = csv.writer(open(stim_fname, mode='w'), delimiter=';', lineterminator='\n')

            if shape_name in ["face_diff_1", "face_diff_2"]:
                diff_level = 3 if shape_name == "face_diff_1" else 5
                face_rule_i = random.randint(0, 20 - diff_level)
                face_outlier_i = face_rule_i + diff_level
                face_rule = "C" + str(face_rule_i).rjust(2, '0') + ".png"
                face_outlier = "C" + str(face_outlier_i).rjust(2, '0') + ".png"
                metadata = [out_pos, diff_level, face_rule, face_outlier, dils, rots]
                for k in range(6):
                    which_face = face_rule if k != out_pos else face_outlier
                    writer_stim.writerow([which_face, refDilations[dils[k]], refAngles_base[rots[k]]])
                writer.writerow([offset, "oddity-faces", stim_fname] + metadata)

            else:
                out_type = randomized_type[i][j]
                metadata = [out_pos, shape_name, dils, rots, out_type]
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
                writer.writerow([offset, "oddity", stim_fname] + metadata)

            offset += 200
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
    shape_file = args["<shape_file>"]
    mini_bloc_size = int(args["<mini_bloc_size>"])
    mini_bloc_repeat = int(args["<mini_bloc_repeat>"])
    face = args["face"]
    generate_csv(s_id, r_id, shape_file, face, mini_bloc_size, mini_bloc_repeat)
