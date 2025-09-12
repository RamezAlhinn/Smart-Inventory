from setuptools import setup, find_packages

setup(
    name="smart_inventory",
    version="0.1",
    packages=find_packages(include=["packages", "packages.*"]),
)