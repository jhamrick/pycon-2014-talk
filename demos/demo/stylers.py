import numpy as np
from pandac.PandaModules import TextureStage, TexGenAttrib
from libpanda import Vec2


class GSOStyler(object):

    def __init__(self, loader, render=None):
        self.loader = loader
        self.render = render

    def _rso(self, gso):
        # use a random seed based on the block's name, so we can have
        # "random" properties that are actually always the same for
        # any given block
        rso = np.random.RandomState(abs(hash(repr(gso))))
        return rso

    def floor(self, gso):
        gso.setColor((0.3, 0.3, 0.3, 1))

    def ry_floor(self, gso):
        tex = self.loader.loadTexture("wood_floor_tex_0.jpg")
        ts = TextureStage.getDefault()
        gso.setTexGen(ts, TexGenAttrib.MWorldPosition)
        gso.setTexProjector(ts, self.render, gso)
        gso.setTexture(ts, tex)
        gso.setTexScale(ts, Vec2(0.25, 0.25) * 10.)
        gso.setColor((0.99, 0.99, 0.99, 1.))

    def original(self, gso):
        gso.destroy_resources(tags=("model",))
        gso.set_model("wood_block")
        gso.init_resources(tags=("model",))
        gso.setScale(0.5, 1. / 6., 0.5)

    def apply(self, gso, style, **kwargs):
        style_func = getattr(self, style)
        style_func(gso, **kwargs)


class PSOStyler(object):

    def floor(self, pso):
        pso.setPos((0, 0, -0.5))

    def ry_floor(self, pso):
        pso.setScale(10, 10, 0.1)
        # half the height of the cylinder, minus the height of the
        # actual table the blocks are on
        pso.setPos((0, 0, -0.05 - 1.2))

    def original(self, pso):
        pass

    def apply(self, pso, style, **kwargs):
        style_func = getattr(self, style)
        style_func(pso, **kwargs)
