#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import expyriment

def init_arguments(args):
    # Sets some arguments because I don't know how to force docopt to do it
    args["--text-size"] = int(args["--text-size"])
    if args["--background-color"]:
        args["bg_color"] = (int(args["BACK_R"]),
                            int(args["BACK_G"]),
                            int(args["BACK_B"]))
    else:
        args["bg_color"] = (0, 0, 0)

    if args["--stimuli-color"]:
        args["stimuli_color"] = (int(args["TEXT_R"]),
                              int(args["TEXT_G"]),
                              int(args["TEXT_B"]))
    else:
        args["stimuli_color"] = (127, 127, 127)

    if args["--window-size"]:
        args["window_size"] = (int(args["WINDOW_W"]), int(args["WINDOW_H"]))
    else:
        args["window_size"] = (1220, 700)
    subject_id = None if (args["--subject-id"] is None) else int(args["--subject-id"])
    if args["--subject-id"] is not None:
        args["--subject-id"] = int(args["--subject-id"])



def init_expyriment(args):
    """Given the CLI arguments, initialize the experiment"""

    expyriment.control.defaults.window_mode = True
    # expyriment.control.defaults.window_size = args["window_size"]
    expyriment.design.defaults.experiment_background_colour = args["bg_color"]
    expyriment.control.defaults.fast_quit = False
    expyriment.control.defaults.initialize_delay = 0
    exp = expyriment.design.Experiment(name=args["--exp-name"])
    exp.add_data_variable_names(['condition',
                                 'time',
                                 'stype',
                                 'id',
                                 'target_time'])
    expyriment.control.initialize(exp)
    exp.clock.wait(400)
    return exp

