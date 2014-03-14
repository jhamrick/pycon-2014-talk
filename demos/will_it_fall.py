#!/usr/bin/env python

from path import path
from panda3d.core import NodePath
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText, TextNode
from demo.viewer import ViewTowers

import numpy as np


class StabilityExperiment(ViewTowers):

    def __init__(self, *args, **kwargs):
        ViewTowers.__init__(self, *args, **kwargs)

        # ignore keys set by viewer
        for key in self.getAllAccepting():
            if key in ("s", "escape"):
                continue
            self.ignore(key)
        self.permanent_events = self.getAllAccepting()

        # global variables
        self.text_bg = (1, 1, 1, 0.7)
        self.font = self.loader.loadFont('cmr12.egg')
        self.question = [
            "Will this tower fall?",
            [[1, "definitely will not fall"],
             [2, "probably will not fall"],
             [3, "might not fall"],
             [4, "don't know"],
             [5, "might fall"],
             [6, "probably will fall"],
             [7, "definitely will fall"]]]
        self.question_keys = ["1", "2", "3", "4", "5", "6", "7"]
        self.choice_text_start = 0.65
        self.feedback_time = 3.0
        self.buffer_time = 0.75

        # create text
        self.create_all_text()

    def run(self):
        # Show the start screen
        self.toggle_task("show_start_screen")
        # Call parent's run().
        ShowBase.run(self)

    def create_all_text(self):
        self.continue_text = OnscreenText(**{
            "text": (
                "In a moment, you will be asked the question displayed on "
                "the left.  When you are ready, press the spacebar to begin."),
            "style": 1,
            "fg": (.75, 0, 0, 1),
            "bg": self.text_bg,
            "pos": (.4, .4),
            "align": TextNode.ACenter,
            "scale": .08,
            "font": self.font,
            "wordwrap": 20
        })
        self.text_parent = self.continue_text.getParent()
        self.continue_text.detachNode()

        xpos = -1.25
        skip = .15
        self.question_text = OnscreenText(**{
            "text": self.question[0],
            "style": 1,
            "fg": (0, 0, .8, 1),
            "bg": self.text_bg,
            "pos": ((xpos + .05), .8),
            "align": TextNode.ALeft,
            "scale": .075,
            "font": self.font,
            "wordwrap": 35})

        self.question_choice_text = []
        for i in xrange(len(self.question[1])):
            n = len(self.question[1]) - i - 1
            ypos = self.choice_text_start - (skip * n)

            t1 = OnscreenText(**{
                "text": "%s" % self.question[1][i][0],
                "style": 1,
                "fg": (0, .1, 0, 1),
                "bg": self.text_bg,
                "pos": ((xpos + .1), ypos),
                "align": TextNode.ALeft,
                "scale": .075,
                "font": self.font})

            t2 = OnscreenText(**{
                "text": "%s" % self.question[1][i][1],
                "style": 1,
                "fg": (0, .1, 0, 1),
                "bg": self.text_bg,
                "pos": ((xpos + 0.17), ypos),
                "align": TextNode.ALeft,
                "scale": .05,
                "font": self.font})

            t = NodePath("choice_%s" % i)
            t.reparentTo(self.text_parent)
            t1.reparentTo(t)
            t2.reparentTo(t)
            self.question_choice_text.append(t)

        for t in self.question_choice_text:
            t.detachNode()

        self.trials_remaining_text = OnscreenText(**{
            "text": "",
            "style": 1,
            "fg": (0, 0, 0, 1),
            "bg": self.text_bg,
            "pos": (-xpos, -.95),
            "align": TextNode.ARight,
            "scale": .05,
            "font": self.font})

    def show_start_screen(self, task):
        self.continue_text.reparentTo(self.text_parent)
        for t in self.question_choice_text:
            t.reparentTo(self.text_parent)
        self.accept("space", self.toggle_task, ["show_trial"])

    def show_trial(self, task):
        if self.sso is None:
            self.goto_sso(0)
        elif self.ssos.index(self.sso) == (self.n_ssos - 1):
            self.exit()
        else:
            self.next()

        n = self.n_ssos - self.ssos.index(self.sso)
        self.trials_remaining_text.setText("Trials remaining: %d" % n)

        self.continue_text.detachNode()
        for t in self.question_choice_text:
            t.detachNode()

        self.camera_rot.setH(np.random.randint(0, 360))
        self.cam_spin = 270

        self.taskMgr.doMethodLater(self.buffer_time, self.rotate, "rotate")

    def rotate(self, task):
        """ Task: rotate camera."""
        H = (self.camera_rot.getH() + 1) % 360
        self.camera_rot.setH(H)
        self.cam_spin -= 1
        if self.cam_spin == 0:
            self.toggle_task("show_question")
            return task.done
        else:
            return task.cont

    def show_question(self, task):
        for t in self.question_choice_text:
            t.reparentTo(self.text_parent)
        for key in self.question_keys:
            self.accept(key, self.record_response, [key])

    def record_response(self, key):
        for k in self.question_keys:
            self.ignore(k)
        for i, t in enumerate(self.question_choice_text):
            if i != (int(key) - 1):
                t.detachNode()
        self.toggle_task("physics")

    def physics(self, task):
        """ Task: simulate physics."""
        # Elapsed time.
        dt = self._get_elapsed() - self.old_elapsed
        # Update amount of time simulated so far.
        self.old_elapsed += dt
        # Step the physics dt time.
        size_sub = self.bbase.sim_par["size_sub"]
        n_subs = int(dt / size_sub)
        self.bbase.step(dt, n_subs, size_sub)

        if self.old_elapsed >= self.feedback_time:
            self.toggle_task("show_trial")
            return task.done
        else:
            return task.cont


if __name__ == "__main__":
    stims = path("stimuli/will_it_fall").listdir()
    stimtypes = ["original" for x in stims]
    StabilityExperiment.create(stimulus=stims, stimtype=stimtypes)
