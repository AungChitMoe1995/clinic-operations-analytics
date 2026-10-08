"""
app.py
------
Entry point alias pointing directly to streamlit_app.py.
Ensures zero-configuration deployment on Streamlit Community Cloud (https://share.streamlit.io/).
"""

import runpy
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")
    runpy.run_path(app_path, run_name="__main__")
