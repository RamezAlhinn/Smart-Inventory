import os, importlib

def get_domain_module(module_name):
    domain = os.getenv("DOMAIN", "supermarket")
    return importlib.import_module(f"src.domains.{domain}.{module_name}")
