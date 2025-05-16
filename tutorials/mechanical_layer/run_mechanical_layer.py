"""Docstring to add."""

import ctypes
import pathlib
from typing import cast

# Load the shared library into ctypes
# Change the paths below if you are running the library from elsewhere
libname = str(pathlib.Path().absolute().parent / "src" / "mechanical_layer" / "build" / "libCrowdMechanics.dylib")
c_lib = ctypes.CDLL(libname)

# Input of the CrowdMechanics main function
files = [
    b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/trial/Parameters.xml",
    b"Materials.xml",
    b"Geometry.xml",
    b"Agents.xml",
    b"AgentDynamics.xml",
]
# Convert the files variable to something ctypes will understand
nFiles = len(files)
filesInput = cast(list[ctypes.c_char_p | bytes | None], (ctypes.c_char_p * nFiles)())
filesInput[:] = files

# The following two lines are optional, they tell ctypes
# what is the type of the input and output variables
## c_lib.CrowdMechanics.argtypes = [ctypes.POINTER(ctypes.c_char_p * nFiles)]
## c_lib.CrowdMechanics.restype = ctypes.c_int

# The actual call to the library
c_lib.CrowdMechanics(filesInput)
