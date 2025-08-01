# /usr/bin/env python3
import setuptools
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mailbagit",
    version="0.7.4",
    author="Gregory Wiedeman",
    author_email="gwiedeman@albany.edu",
    description="A tool for preserving email in multiple preservation formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UAlbanyArchives/mailbag",
    packages=setuptools.find_namespace_packages(exclude=("tests")),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["mailbagit=mailbagit:cli", "mailbagit-gui=mailbagit:gui", "mailbagit-guided=mailbagit:guided"]},
    install_requires=[
        "bagit>=1.8.1,<2",
        "beautifulsoup4>=4.11.1,<5",
        "black>=23.7,<26",
        "jsonmodels>=2.2,<=2.5.0",
        "extract_msg>=0.42.0",
        "structlog>=21.1.0,<22",
        "packaging>=21.0,<25",
        "python-json-logger>=2.0.2,<3",
        "pyparsing>=2.1.0,<3",
        "pytest>=7.0.1,<8",
        "python-dotenv>0.19.0,<=0.19.1",
        "chardet>=4.0.0,<5",
        "warcio>=1.7.4,<2",
        "requests >=2.27.1,<3",
        "cssutils >=2.4.2,<3",
        "python-json-logger >=2.0.2,<3",
    ],
    extras_require={
        "gui": ["gooey>=1.0.8.1,<2"],
        "pst": ["libpff-python==20231205"],
        "dev": ["pyinstaller==5.0.1,<6"],
    },
    python_requires=">=3.9",
)
