#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Wrapper around expyriment to turn a csv file into a time accurate experiment

This is meant to be a simple wrapper around expyriment that takes a csv file
containing stimuli and onsets and displays them in a time accurate way while
recording all inputs. It's based on Christophe Pallier's
"localizer_standard.py" and was superficially modified by Mathias Sablé-Meyer
to be easier to hack into.

Reach out for help with this!

usage:
    launcher.py calibrate
    launcher.py [(--stimuli-color TEXT_R TEXT_G TEXT_B)]
                [(--background-color BACK_R BACK_G BACK_B)]
                [(--window-size WINDOW_W WINDOW_H)]
                [options] [--] <file> ...

optional arguments:
  -h, --help              Show this help message and exit
  --subject-id SUBJECT_ID ID of the starting subject
  --stim-dir STIM_DIR     Directory to look for stimuli [default: STIM_DIR/]
  --exp-name EXP_NAME     Name of the experiment        [default: "Default"]
  --text-font TEXT_FONT   Font to use to display text   [default: "dejavusans"]
  --text-size TEXT_SIZE   Font size used for text       [default: 48]
"""

import os.path
import csv
import queue
import expyriment
import docopt
import initialize

# Used for fast tuple-parsing in loading shapes vertices
from ast import literal_eval
# Used for stimuli in circle in oddity
from math import sin, cos, pi


def calibration(exp, args):
    """This function does the calibration. Put in module if too long."""
    show_text("Nous allons faire un calibrage", args).present()
    exp.clock.wait(1500)
    expyriment.stimuli.FixCross(size=(25, 25),
                                line_width=3,
                                colour=args["stimuli_color"]).present()
    exp.clock.wait(2100)


def show_text(text, args):
    """Given some string and parameters, prepare a text to show

    This returns an expyriment TextLine and requires the second arguments to
    have a few relevant attributes, typically it should be the output of
    parsing the CLI arguments.
    """
    return expyriment.stimuli.TextLine(text,
                                       text_font=args["--text-font"],
                                       text_size=args["--text-size"],
                                       text_colour=args["stimuli_color"],
                                       background_colour=args["bg_color"])


def load_stimuli(stype, f, bp, args):
    """Does what is appropriate to preload a stimuli based on its "stype" """
    stimulus = None
    if stype == "picture":
        stimulus = expyriment.stimuli.Picture(os.path.join(bp, f))
    elif stype == 'sound':
        stimulus = expyriment.stimuli.Audio(os.path.join(bp, f))
    elif stype == 'video':
        stimulus = expyriment.stimuli.Video(os.path.join(bp, f))
    elif stype == 'text':
        stimulus = show_text(f, args)
    elif stype == 'dot' or stype == 'circle':
        r, line_width, px, py = f.split(";")
        stimulus = expyriment.stimuli.Circle(int(r),
                                             colour=args["stimuli_color"],
                                             line_width=int(line_width),
                                             position=(float(px), float(py)),
                                             anti_aliasing=10)
    elif stype == 'shape':
        line_width, px, py, *v_list = [literal_eval(x) for x in f.split(";")]
        shape = expyriment.stimuli.Shape(position=(int(px), int(py)),
                                         colour=args["stimuli_color"],
                                         line_width=int(line_width),
                                         anti_aliasing=10)
        shape.add_vertices(v_list)
        stimulus = shape
    if stype == "small_star":
        px, py, path = f.split(";")
        stimulus = expyriment.stimuli.Picture(os.path.join(bp, path),
                                              position=(float(px), float(py)))
    elif stype == "oddity":
        canvas = expyriment.stimuli.Canvas(args["window_size"])
        fpath = os.path.join(bp, f)
        dist = 200
        alpha = 2*pi/6
        for i, shape in enumerate(csv.reader(open(fpath), delimiter=';')):
            v_list = [literal_eval(x) for x in shape]
            px, py = [dist * f(i*alpha) for f in [cos, sin]]
            shape = expyriment.stimuli.Shape(position=(int(px), int(py)),
                                             colour=args["stimuli_color"],
                                             line_width=0,
                                             anti_aliasing=10)
            shape.add_vertices(v_list)
            shape.plot(canvas)
        stimulus = canvas
    elif stype == 'fix':
        stimulus = expyriment.stimuli.FixCross(size=(25, 25),
                                               line_width=3,
                                               colour=args["stimuli_color"])
    elif stype == 'blank':  # This should be distinguished from fixation?
        return expyriment.stimuli.BlankScreen()
    # canvas = expyriment.stimuli.Canvas(args["window_size"])
    # fix = expyriment.stimuli.FixCross(size=(25, 25),
    #                                     line_width=3,
    #                                     colour=args["stimuli_color"])
    # fix.plot(canvas)
    # stimulus.plot(canvas)
    return stimulus


def main():
    """This is the main function that does the heavy-lifting"""

    args = docopt.docopt(__doc__, version='0.0.1')

    # Initialize expyriment & wait its message to show
    initialize.init_arguments(args)
    exp = initialize.init_expyriment(args)

    # Useful shortcuts throughout the file
    kb = expyriment.io.Keyboard()

    # If we need to calibrate, then do so and terminate.
    if args["calibrate"]:
        calibration(exp, args)
        expyriment.control.end('Merci !', 2000)
        return 0

    # Hash table for fast retrieval when presenting: reading from disk is slow!
    hash_table = dict()

    # Now let's read the csv file line by line and populate the events.
    # PriorityQueue sort on insertion based on the first element of the
    # inserted tuple: this means your csv file can have random order, or that
    # you can take input from several csv files
    events = queue.PriorityQueue()
    for csv_file in args["<file>"]:
        # Save the path to the CSV file
        exp.add_experiment_info(csv_file)

        # Create the path to the stimuli
        bp = os.path.join(os.path.dirname(csv_file), args["--stim-dir"])

        # Open the csv file and read its rows.
        # ATTENTION : Encoding is platform dependant. See the open() manual
        for row in csv.reader(open(csv_file), delimiter='\t'):
            # Destruct a row into its parts, they will be of type str
            cond, onset, stype, f = row

            # If this is the first encounter of this stimuli then preload it
            if (stype, f) not in hash_table:
                hash_table[stype, f] = load_stimuli(stype, f, bp, args)
                hash_table[stype, f].preload()

            # Then push relevant events based on the type
            events.put((int(onset), cond, stype, f, (stype, f)))

    expyriment.control.start(skip_ready_screen=True,
                             subject_id=args["--subject-id"])

    show_text("Waiting for scanner sync (or press 't')", args).present()
    kb.wait_char('t')

    # Start the experiment clock and loop through the events
    clock = expyriment.misc.Clock()
    while not events.empty():
        onset, cond, stype, id, (stype, f) = events.get()

        # If it's still too early, then wait for the onset but log keypresses
        while clock.time < (onset - 1):
            # clock.wait(1) why though? Shouldn't we run as fast as we can?
            k = kb.check()
            if k is not None:
                exp.data.add([clock.time, f"keypressed,{k}"])

        # When time has come, present the stimuli and log that you just did so
        # Essayer de synchroniser ça avec les flips
        hash_table[stype, f].present()
        exp.data.add([f"{cond}", clock.time, f"{stype},{id},{onset}"])

    # Now the experiment is done, terminate the exp
    expyriment.control.end('Merci !', 2000)
    return 0


if __name__ == '__main__':
    main()
