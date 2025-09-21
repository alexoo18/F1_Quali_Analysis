# run_app.py
import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    script = os.path.abspath("main.py")
    sys.argv = ["streamlit", "run", script, "--server.runOnSave=true"]
    sys.exit(stcli.main())

