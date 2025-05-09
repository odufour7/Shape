# Minimal Crowd Simulation Example

Follow these steps to run a minimal example of a crowd simulation:

---

## 1. Create Result Folders

Create two directories to store simulation results:

- `Dynamic`
- `Static`

You can do this from the terminal:
```bash
mkdir Dynamic Static
```

---

## 2. Export Crowd Configuration Files

1. Open the [**Streamlit app**](https://crowdmecha.streamlit.app/).
2. Go to the **Crowd** tab.
3. Click **"Initialize your own crowd"**.
4. In the sidebar at the bottom, click **"Export crowd as XML config files"**.
5. Download the XML files and save them in an appropriate location.

---

## 3. Create a `Parameters.xml` File

Create a `Parameters.xml` file specifying the absolute paths to your `Static` and `Dynamic` directories. Use the following template (replace the paths with your actual folder locations):

```xml
<?xml version="1.0" encoding="utf-8"?>
<Parameters>
    <Directories Static="/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/tutorials/mechanical_layer/Static/" Dynamic="/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/tutorials/mechanical_layer/Dynamic/"/>
    <Times TimeStep="0.1" TimeStepMechanical="1e-5"/>
</Parameters>
```

---

## 4. Build the C++ Project

Navigate to the root of the `mechanical_layer` repository and build the project:

```bash
cmake -H. -Bbuild -DBUILD_SHARED_LIBS=ON
cmake --build build
```

---

## 5. Run the Python Simulation Script

Within the `mechanical_layer` directory, run the following Python code (adapt as needed):

```python
import ctypes
import pathlib

# Load the shared library into ctypes
#   Change the paths below if you are runninf the library from elsewhere
libname = str(pathlib.Path().absolute() / "build/libCrowdMechanics.so")
c_lib = ctypes.CDLL(libname)

# Input of the CrowdMechanics main function
files = [
    b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/tutorials/mechanical_layer/Parameters.xml",
    b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/data/xml/crowd_ANSURII_tutorial/Materials.xml",
    b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/data/xml/crowd_ANSURII_tutorial/Geometry.xml",
    b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/data/xml/crowd_ANSURII_tutorial/Agents.xml",
    b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/data/xml/crowd_ANSURII_tutorial/AgentDynamics.xml",
]
# Convert the files variable to something ctypes will understand
nFiles = len(files)
filesInput = (ctypes.c_char_p * nFiles)()
filesInput[:] = files

# The following two lines are optional, they tell ctypes
# what is the type of the input and output variables
## c_lib.CrowdMechanics.argtypes = [ctypes.POINTER(ctypes.c_char_p * nFiles)]
## c_lib.CrowdMechanics.restype = ctypes.c_int

# The actual call to the library
c_lib.CrowdMechanics(filesInput)
```

---

## Summary

1. **Create** `Static` and `Dynamic` folders.
2. **Export** crowd XML files from the [Streamlit app](https://crowdmecha.streamlit.app/).
3. **Write** your `Parameters.xml` with correct paths.
4. **Build** the C++ project.
5. **Run** your simulation using Python or directly via the executable.
