Run the app locally
===================

To set up, follow these steps after downloading the repository from GitHub:

**1. Environment Setup**

Create and activate a virtual environment to manage dependencies efficiently:

.. code-block:: bash

   # Upgrade pip to the latest version
   python -m pip install --upgrade pip
   # Install 'uv' for managing dependencies
   pip install uv
   # Synchronize dependencies as specified in your project
   uv sync


**2. Launch the App**

Start the app with the following command:

.. code-block:: bash

   uv run streamlit run src/streamlit_app/app/app.py