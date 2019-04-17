#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script for the MRI Geometry experiment

Blabla
"""

import csv
import os
import random
import numpy as np


def generate_csv(path):
    """Blabla This is useful"""
    writer = csv.writer(open('output.csv', mode='w'), delimiter='\t',)
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
    for dirs in dirs_list:
        bp = os.path.join("STIM_DIR", dirs)
        if dirs == 'checker':
            files = np.tile(["checker01.png", "checker02.png"], 10)
        else:
            files = [os.path.join(dirs, f)
                     for f in os.listdir(bp)
                     if os.path.isfile(os.path.join(bp, f))]
            random.shuffle(files)
        for i, f in enumerate(files):
            writer.writerow(["test", offset, "picture", f])
            offset += 150
            writer.writerow(["test", offset, "picture", "stimblank.png"])
            offset += 350
            if (count[dirs], i) in positions[dirs]:
                writer.writerow(["test", offset, "picture", "Star.png"])
                offset += 150
                writer.writerow(["test", offset, "picture", "stimblank.png"])
                offset += 350
        offset += 4000 + (random.randint(0, 2) * 2000)
        count[dirs] += 1
    print(f"Total duration is {offset/1000/60}min")


if __name__ == "__main__":
    generate_csv("")
