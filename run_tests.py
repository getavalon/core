import sys
import time
import types

maya = types.ModuleType("maya")
maya.mel = types.ModuleType("mel")
maya.cmds = types.ModuleType("cmds")

maya.cmds.ls = lambda *args, **kwargs: ["pCube1"]
maya.mel.eval = lambda string: None

sys.modules["maya"] = maya

if __name__ == '__main__':
    import nose
    argv = sys.argv[:]
    argv.extend(['-c', '.noserc'])
    nose.main(argv=argv)
