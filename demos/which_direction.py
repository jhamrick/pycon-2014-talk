#!/usr/bin/env python

from path import path
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionRay
from pandac.PandaModules import LineSegs, AmbientLight
from direct.gui.OnscreenText import OnscreenText, TextNode
from demo.viewer import ViewTowers

import numpy as np


class DirectionExperiment(ViewTowers):

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
        self.question = (
            "Use the mouse to indicate the direction that "
            "the tower will fall.")
        self.feedback_time = 3.0
        self.buffer_time = 0.75

        # create text
        self.create_all_text()

        # create direction line
        self.line = LineSegs()
        self.line_node = None
        self.angle = None

        alight = AmbientLight('alight3')
        alight.setColor((0.8, 0.8, 0.8, 1))
        self.line_light = self.lights.attachNewNode(alight)

    def place_camera(self):
        self.cameras.setPos(0, -12, 2.5)
        self.look_at.setPos(0, 0, 1.5)
        self.cameras.lookAt(self.look_at)

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
        self.question_text = OnscreenText(**{
            "text": self.question,
            "style": 1,
            "fg": (0, 0, .8, 1),
            "bg": self.text_bg,
            "pos": ((xpos + .05), .8),
            "align": TextNode.ALeft,
            "scale": .075,
            "font": self.font,
            "wordwrap": 35})

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
        self.accept("space", self.toggle_task, ["show_trial"])

    def show_trial(self, task):
        if self.line_node is not None:
            self.line_node.removeNode()
            self.line_node = None

        if self.sso is None:
            self.goto_sso(0)
        elif self.ssos.index(self.sso) == (self.n_ssos - 1):
            self.exit()
        else:
            self.next()

        n = self.n_ssos - self.ssos.index(self.sso)
        self.trials_remaining_text.setText("Trials remaining: %d" % n)

        self.continue_text.detachNode()

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
        self.toggle_task("draw_direction")
        self.accept("mouse1", self.record_response)

    def record_response(self):
        self.ignore("mouse1")
        self.taskMgr.remove("draw_direction")
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

    def draw_direction(self, task):
        if self.mouseWatcherNode.hasMouse():
            cv = self._get_collision(self.floor)
            cv = cv / np.linalg.norm(cv)
            self.angle = np.arctan2(cv[1], cv[0])

            sx, sy, sz = self.floor.getScale() / 2.0
            gx, gy, gz = self.floor.getPos()
            gz += sz + 0.01

            if self.line_node is not None:
                self.line_node.removeNode()
                self.line_node = None

            self.line.reset()
            self.line.setColor(1, 1, 1, 1)
            self.line.setThickness(5)
            self.line.moveTo(gx, gy, gz)
            self.line.drawTo(cv[0] * sx, cv[1] * sy, gz)
            self.line_node = self.render.attachNewNode(self.line.create())
            self.line_node.setLight(self.line_light)

        return task.cont

    def _get_collision(self, node, debug=False):
        mx = self.mouseWatcherNode.getMouseX()
        my = self.mouseWatcherNode.getMouseY()
        if debug:
            print "mouse:", (mx, my)

        # get the origin and direction of the ray extending from the
        # camera to the mouse pointer
        cm = np.array(self.cam.getNetTransform().getMat())
        cr = CollisionRay()
        cr.setFromLens(self.cam.node(), (mx, my))
        cp = np.hstack([cr.getOrigin(), 1])
        cd = np.hstack([cr.getDirection(), 0])
        cp = np.dot(cm.T, cp)[:3]
        cd = np.dot(cm.T, cd)[:3]
        if cd[2] > -1:
            cd[2] = -1
        if debug:
            print "direction:", cd
            print "origin:", cp

        # point on the plane, z-axis
        pz = node.getPos(self.render)[2]
        sz = node.getScale(self.render)[2] / 2.0
        p0 = np.array([0, 0, pz + sz])
        if debug:
            print "p0:", p0

        # this is the intersection equation that we want to solve,
        # where s is the point on the line that intersects
        #     e_z(cp + s*cd - p0) = 0
        s = (p0[2] - cp[2]) / cd[2]
        if debug:
            print "s:", s

        # transform the collision point from line coordinates to world
        # coordinates
        cv = cp + s * cd
        if debug:
            print "collision:", cv

        return cv

if __name__ == "__main__":
    stims = [x for x in path("stimuli/which_direction").listdir() if x.endswith(".cpo")]
    stimtypes = ["original" for x in stims]
    DirectionExperiment.create(stimulus=stims, stimtype=stimtypes)
