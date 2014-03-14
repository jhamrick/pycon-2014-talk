from panda3d.core import Filename, getModelPath, loadPrcFile, PandaSystem
from path import path
import scenesim

if PandaSystem.getVersionString() != "1.9.0":
    import warnings
    warnings.warn(
        "You are using a version of Panda3D that may not work "
        "with these demos. If you encounter problems, please try "
        "version 1.9.0 instead.")

# load panda configuration
ROOT_PATH = path(__path__[0]).joinpath("..").abspath()

config_pth = ROOT_PATH.joinpath("Config.prc")
if config_pth.isfile():
    cp = Filename.fromOsSpecific(config_pth)
    cp.makeTrueCase()
    print "Loading config '%s'" % cp
    loadPrcFile(cp)

getModelPath().appendDirectory(ROOT_PATH.joinpath("models"))
getModelPath().appendDirectory(ROOT_PATH.joinpath("textures"))
