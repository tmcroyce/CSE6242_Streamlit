import streamlit as st
import subprocess
import sys
import os

st.title("📦 Package Availability Debug")

st.write("### System Information")
st.code(f"Python version: {sys.version}")
st.code(f"Python executable: {sys.executable}")

# Try importing key packages
packages_to_check = [
    "pandas", 
    "numpy", 
    "scikit-learn", 
    "streamlit", 
    "pickle", 
    "lzma", 
    "pyarrow",
    "h5py"
]

st.write("### Package Import Check")
for package in packages_to_check:
    try:
        exec(f"import {package}")
        st.success(f"✅ Successfully imported {package}")
        # Get version if possible
        try:
            version = eval(f"{package}.__version__")
            st.code(f"{package} version: {version}")
        except:
            st.code(f"{package} version: unknown")
    except ImportError as e:
        st.error(f"❌ Failed to import {package}: {str(e)}")

# List installed packages
st.write("### All Installed Packages")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                           capture_output=True, text=True, check=True)
    installed_packages = result.stdout.strip().split('\n')
    for package in installed_packages:
        st.code(package)
except Exception as e:
    st.error(f"Failed to list installed packages: {str(e)}")

# Get environment variables
st.write("### Environment Variables")
for key, value in os.environ.items():
    st.code(f"{key}={value}")
