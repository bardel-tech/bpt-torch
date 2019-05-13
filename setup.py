import os
from io import open
import subprocess
from setuptools import setup, find_packages

here = os.path.dirname(__file__)

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    install_requires = [l.strip() for l in f.readlines()]
    install_requires = [l for l in install_requires if l]

version = subprocess.check_output(["dev", "query", "{{.Version}}"])


setup(
    name="bpttorch",
    version=version,
    description="Prometheus aggregator",
    long_description=long_description,
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    author="Joshua Forman",
    author_email="jforman@outbrain.com",
    url="http://www.outbrain.com",
    license="MIT",
    packages=["bpt-torch"],
    package_dir={"bpt-torch": "torch"},
    include_package_data=False,
    zip_safe=True,
    install_requires=install_requires,
    entry_points="""
      [console_scripts]
      torch = torch.__main__:main
      """,
)
