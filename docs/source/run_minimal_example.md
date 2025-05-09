# Minimal crowd simulation example

Follow these steps to run a minimal example of a crowd simulation:

---

## 1. Export crowd configuration files

1. Open the [**Streamlit app**](https://crowdmecha.streamlit.app/).
2. Go to the **Crowd** tab.
3. Click **"Initialize your own crowd"**.
4. In the sidebar at the bottom, click **"Export crowd as XML config files"**.
5. Download the XML files and save them in an appropriate location.

---

## 2. Create result folders

Create two directories to store simulation results:
- `Dynamic`
- `Static`

---

## 3. Create a `Parameters.xml` file

Create a `Parameters.xml` file specifying the absolute paths to your `Static` and `Dynamic` directories. Use the following template (replace the paths with your actual folder locations):

```xml
<?xml version="1.0" encoding="utf-8"?>
<Parameters>
    <Directories Static="/AbsolutePath/Static/" Dynamic="/AbsolutePath/Dynamic/"/>
    <Times TimeStep="0.1" TimeStepMechanical="1e-5"/>
</Parameters>
```

---

## 4. Build the C++ project

Navigate to the root of the `mechanical_layer` repository and build the project:

```bash
cmake -H. -Bbuild -DBUILD_SHARED_LIBS=ON
cmake --build build
```

---

## 5. Run the following python simulation script

Within the `mechanical_layer` directory, run the following Python code (adapt as needed) taking care of replacing `/AbsolutePath/` with the correct folder path:

```python
import ctypes
import pathlib

# Load the shared library into ctypes
#   Change the paths below if you are runninf the library from elsewhere
libname = str(pathlib.Path().absolute() / "build/libCrowdMechanics.so")
c_lib = ctypes.CDLL(libname)

# Input of the CrowdMechanics main function
files = [
    b"/AbsolutePath/Parameters.xml",
    b"/AbsolutePath/Materials.xml",
    b"/AbsolutePath/Geometry.xml",
    b"/AbsolutePath/Agents.xml",
    b"/AbsolutePath/AgentDynamics.xml",
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

## 6. Or run the following c++ simulation script

Within the `mechanical_layer` directory, run the following c++ code (adapt as needed) taking care of replacing `/AbsolutePath/` with the correct folder path:

```c++
//  Include the main header of the library
#include "CrowdMechanics.h"

int main(void)
{
    char* files[5] =
        {"/AbsolutePath/Parameters.xml",
         "Materials.xml",
         "Geometry.xml",
         "Agents.xml",
         "AgentDynamics.xml"};
    //  Call the library
    CrowdMechanics(files);

    return 0;
}
```

---

## Summary

1. **Create** `Static` and `Dynamic` folders.
2. **Export** crowd XML files from the [Streamlit app](https://crowdmecha.streamlit.app/).
3. **Write** your `Parameters.xml` with correct paths.
4. **Build** the C++ project.
5. **Run** your simulation using Python or directly via the executable.
