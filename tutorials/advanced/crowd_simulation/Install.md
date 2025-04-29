# Installation guide

The C++ code is meant to be installed as a shared library. Of course, you can also include all sources and headers in your own code and compile everything as a whole. We detail here below the originally intended way.

### Dependencies

We use ```cmake``` as a build system, so make sure you have a recent version installed (https://cmake.org/download/).

### Building the library

Running the following commands will build ```CrowdMechanics``` in the ```build``` directory as a shared library:

```
cmake -H. -Bbuild -DBUILD_SHARED_LIBS=ON
cmake --build build