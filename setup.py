import sys
import os
from setuptools import setup, find_packages
import kathekon

# Ensure Python 3.7+
if sys.version_info < (3, 7):
    sys.exit("ERROR: kathekon requires Python 3.7 or higher.")

# Read the long description from README.md
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "kathekon is a Python library and CLI tool for fetching Stoic quotes with interpretations."


setup(
    name="kathekon",
    version=kathekon.__version__,
    packages=find_packages(exclude=["tests"]),
    author="Jan T. Müller",
    author_email="mail@jantmueller.com",
    description="kathekon is a Python library and CLI tool for fetching Stoic quotes with interpretations.",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/janthmueller/kathekon",
    project_urls={
        "Documentation": "https://github.com/janthmueller/kathekon/blob/main/README.md",
        "Source": "https://github.com/janthmueller/kathekon",
        "Tracker": "https://github.com/janthmueller/kathekon/issues",
    },
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "openai": ["openai>=1.57.0"],
        "all": ["openai>=1.57.0"],
    },
    include_package_data=True,  # Include additional files
    package_data={
        "kathekon": ["data/quotes.db"],  # Ensure quotes.db is included
    },
    entry_points={
        "console_scripts": [
            "kathekon=kathekon.cli:main",  # Single entry point for the CLI
            "stoic-quote=kathekon.cli:main",  # Alias for the CLI
        ],
    },
)
