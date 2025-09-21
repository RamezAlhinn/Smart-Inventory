from setuptools import setup, find_packages

from setuptools import setup, find_packages

setup(
    name="smart-inventory",
    version="0.1.0",
    packages=find_packages(where="src"),  # look inside src/
    package_dir={"": "src"},              # root is src/
    install_requires=[
        "pandas",
        "prophet",
        "streamlit",
        # add other dependencies from requirements.txt if needed
    ],
) 