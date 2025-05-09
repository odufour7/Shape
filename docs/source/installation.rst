Installation guide
==================

You can try out the Streamlit application online at the `app <https://crowdmecha.streamlit.app/>`_, generate your own crowd, download the associated configuration files, and run the crowd simulation locally.

If you want to use the Streamlit application locally, you can install it and follow the advanced tutorial :ref:`installation_guide_app`.

The C++ code is intended to be installed as a shared library. Alternatively, you can include all sources and headers directly in your own code and compile everything together. Below, we detail the originally intended installation method.

Dependencies
------------

This project uses ``cmake`` as the build system. Please ensure you have a recent version installed. You can download it from the `official site <https://cmake.org/download/>`_.

Building the Library
--------------------

To build the ``CrowdMechanics`` library as a shared library in the ``build`` directory, run the following commands:

.. code-block:: console

    cmake -H. -Bbuild -DBUILD_SHARED_LIBS=ON
    cmake --build build

