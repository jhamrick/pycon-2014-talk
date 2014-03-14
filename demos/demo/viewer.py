# Builtin
from copy import deepcopy
import random
# External
import numpy as np
# Panda3D
import pandac.PandaModules as pm
import panda3d.core as p3d
# Scenesim
from scenesim.display.viewer import Viewer
from scenesim.display.viewer import load as load_ssos
from scenesim.display.viewer import setup_bullet as _setup_bullet
from scenesim.objects.gso import GSO
from scenesim.objects.pso import RBSO

from stylers import GSOStyler, PSOStyler


class ViewTowers(Viewer):

    @staticmethod
    def setup_bullet():
        bbase = _setup_bullet()
        return bbase

    @classmethod
    def create(cls, **options):
        # setup Bullet physics
        bbase = cls.setup_bullet()

        # create the instance
        app = cls(options)
        app.init_physics(bbase)
        app.init_ssos()
        app.run()

    def __init__(self, options):

        Viewer.__init__(self)

        self.options = deepcopy(options)

        self.place_camera()
        self.create_lights()
        self.win.setClearColor((0.05, 0.05, 0.1, 1.0))
        self.disableMouse()

        self.stimtype = None
        self._prop_cache = None

    def place_camera(self):
        self.cameras.setPos(0, -8, 2.75)
        self.look_at.setPos(0, 0, 1.5)
        self.cameras.lookAt(self.look_at)

    def create_lights(self):
        # function for converting cylindrical coordinates to cartesian
        # coordinates
        rtz2xyz = lambda r, t, z: (r * np.cos(t), r * np.sin(t), z)

        # positions for point lights
        plight_pos = [
            rtz2xyz(1.5, 4 * np.pi / 12., 0),
            rtz2xyz(1.5, 12 * np.pi / 12., 0),
            rtz2xyz(1.5, 20 * np.pi / 12., 0),
            (0, 0, 1.3),
        ]

        # create point lights
        self.plights = p3d.NodePath("plights")
        for i, pos in enumerate(plight_pos):
            plight = pm.PointLight('plight%d' % i)
            plight.setColor((0.5, 0.5, 0.5, 1.0))
            plight.setAttenuation((0, 0, 0.5))
            plnp = self.plights.attachNewNode(plight)
            plnp.setPos(pos)
            self.render.setLight(plnp)
        self.plights.reparentTo(self.lights)
        self.plights.setPos(0, 0, 4 / 3.)

        # update the position and color of the spotlight
        slnp = self.lights.find('slight')
        slnp.setPos((8, 6, 20))
        slnp.lookAt(self.look_at)
        slnp.node().setColor((1, 1, 1, 1))

        # update the color of the ambient light
        alnp = self.lights.find('alight')
        alnp.node().setColor((0.2, 0.2, 0.2, 1))

    @property
    def curr_gsos(self):
        return self.sso.descendants(type_=GSO, names="block")

    @property
    def curr_psos(self):
        return self.sso.descendants(type_=RBSO, names="block")

    def _store_props(self):
        props = []
        for gso in self.curr_gsos:
            color = gso.getColor()
            model = gso.get_model()
            props.append({'color': color, 'model': model})
        self._prop_cache = props

    def _apply_props(self):
        self.sso.destroy_tree(tags=("model",))
        props = deepcopy(self._prop_cache)
        for gso in self.curr_gsos:
            prop = props.pop(0)
            gso.apply_prop(prop)
        self.sso.init_tree(tags=("model",))
        styler = GSOStyler(self.loader)
        for gso in self.curr_gsos:
            styler.apply(gso, self.stimtype)

    def init_ssos(self):
        """ Initialize the ssos."""

        # load the actual sso objects from disk and do the default
        # Viewer initialization
        ssos = load_ssos(self.options['stimulus'])
        random.shuffle(ssos)
        Viewer.init_ssos(self, ssos)

        # initialize the floor sso
        floor_path = "stimuli/round-wooden-floor.cpo"
        self.floor = load_ssos([floor_path])[0]
        gso, = self.floor.descendants(type_=GSO)
        PSOStyler().apply(self.floor, "floor")
        GSOStyler(self.loader).apply(gso, "floor")
        self.floor.reparentTo(self.scene)
        self.floor.init_tree(tags=("model", "shape"))

        # give it a little extra ambient light
        alight = pm.AmbientLight('alight2')
        alight.setColor((0.6, 0.6, 0.6, 1.0))
        alnp = self.lights.attachNewNode(alight)
        self.floor.setLight(alnp)

    def optimize_camera(self):
        pass

    def goto_sso(self, i):
        if self._prop_cache:
            self._prop_cache = None

        self.stimtype = self.options['stimtype'][i]

        Viewer.goto_sso(self, i)

        self._store_props()
        self._apply_props()

        minb, maxb = self.sso.getTightBounds()
        height = max(3, maxb[2])
        self.plights.setPos(0, 0, height * 2 / 3.)

        print "Showing sso '%s'" % self.sso.getName()

    def attach_physics(self):
        styler = PSOStyler()
        for pso in self.curr_psos:
            styler.apply(pso, self.stimtype)
        Viewer.attach_physics(self)

    def physics(self, task):
        """Task: simulate physics."""
        # Elapsed time.
        dt = self._get_elapsed() - self.old_elapsed
        # Update amount of time simulated so far.
        self.old_elapsed += dt
        # Step the physics dt time.
        size_sub = 1. / 1000.
        n_subs = int(dt / size_sub)
        self.bbase.step(dt, n_subs, size_sub)
        return task.cont
