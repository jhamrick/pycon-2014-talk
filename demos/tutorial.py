from path import path

# this loads the configuration in Config.prc
from panda3d.core import Filename, getModelPath, loadPrcFile
config_pth = path("Config.prc")
if config_pth.isfile():
    cp = Filename.fromOsSpecific(config_pth)
    cp.makeTrueCase()
    print "Loading config '%s'" % cp
    loadPrcFile(cp)

getModelPath().appendDirectory("models")
getModelPath().appendDirectory("textures")


import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletWorld
from panda3d.bullet import BulletDebugNode


class BlockTutorial(ShowBase):

    def __init__(self):
        # Step 2: Set up graphics
        ShowBase.__init__(self)
        self.setup_camera()
        self.load_block_model()

        # Step 3: Set up physics
        self.create_physics()
        self.load_block_physics()

        # Step 4: Link graphics and physics
        self.link()

        # This lets us see the debug skeletons for the physics objects.
        self.setup_debug()

        # Setup keybindings
        print
        print "Keybindings"
        print "-----------"

        # Turn on/off the debug skeletons by pressing 'd'
        self.accept('d', self.toggle_debug)
        print "d\t: toggle debug mode"

        # Turn on/off physics simulation by pressing 'space'
        self.accept('space', self.toggle_physics)
        print "space\t: toggle physics"

        # Exit the application by pressing 'esc'
        self.accept('escape', sys.exit)
        print "esc\t: exit"

    def setup_camera(self):
        """Position the camera so we can see the objects in the scene"""

        self.cam.set_pos(-8, -6, 2.75)
        self.cam.look_at((0, 0, 0))

    def load_block_model(self):
        """Load the 3D model of a block, and tell Panda3D to render it"""

        self.block_graphics = self.loader.loadModel("wood_block.egg")
        self.block_graphics.reparent_to(self.render)
        self.block_graphics.set_scale(0.2, 0.2, 0.2)

    def create_physics(self):
        """Create the physical world, and start a task to simulate physics"""

        self.world = BulletWorld()
        self.world.set_gravity((0, 0, -9.81))

        self.physics_on = False
        self.taskMgr.add(self.step_physics, "physics")

    def step_physics(self, task):
        """Get the amount of time that has elapsed, and simulate physics for
        that amount of time"""

        if self.physics_on:
            dt = globalClock.get_dt()
            self.world.do_physics(dt)
        return task.cont

    def toggle_physics(self):
        """Turn physics on or off."""

        self.physics_on = not(self.physics_on)

    def load_block_physics(self):
        """Create collision geometry and a physical body for the block."""

        self.block_body = BulletRigidBodyNode('block-physics')
        self.block_body.add_shape(BulletBoxShape((0.2, 0.6, 0.2)))
        self.block_body.set_mass(1.0)
        self.world.attach_rigid_body(self.block_body)

    def link(self):
        """Tell Panda3D that the block's physics and graphics should be
        linked, by making the physics NodePath be the parent of the
        graphics NodePath.

        """

        self.block_physics = self.render.attach_new_node(self.block_body)
        self.block_graphics.reparent_to(self.block_physics)

    def setup_debug(self):
        """Set up a debug node, which will render skeletons for all the
        physics objects in the physics world."""

        debug_node = BulletDebugNode('Debug')
        debug_node.show_wireframe(True)
        debug_node.show_constraints(True)
        debug_node.show_bounding_boxes(True)
        debug_node.show_normals(True)
        self.world.set_debug_node(debug_node)
        self.debug_np = self.render.attach_new_node(debug_node)

    def toggle_debug(self):
        """Turn off/on rendering of the physics skeletons."""
        if self.debug_np.is_hidden():
            self.debug_np.show()
            # simulate physics for a tiny amount of time, because the
            # skeletons won't actually be rendered until physics has
            # started
            self.world.do_physics(0.0000001)
        else:
            self.debug_np.hide()


if __name__ == "__main__":
    app = BlockTutorial()
    app.run()
